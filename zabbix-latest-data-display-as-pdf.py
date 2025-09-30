import requests
import datetime
from collections import defaultdict
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import os

# --- CONFIG ---
ZABBIX_URL = "http://your_zabbix_host/api_jsonrpc.php"
USERNAME = "username"
PASSWORD = "password"

ITEM_KEYS = {
    "CPU Usage (%)": "system.cpu.util[,user]",
    "Memory Usage (%)": "vm.memory.util",
    # "Disk Usage (%)": "vfs.fs.size",
}

OUTPUT_PDF = "zabbix_selected_groups_report.pdf"
CHART_DIR = "charts"

if not os.path.exists(CHART_DIR):
    os.makedirs(CHART_DIR)

# Selected host groups
GROUPS = [
    {"groupid": "Host_groupid", "name": "Host_groupname"},
    #{"groupid": "Host_groupid", "name": "Host_groupname"},
    #{"groupid": "Host_groupid", "name": "Host_groupname"},
]

# --- LOGIN ---
def zabbix_login():
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {"username": USERNAME, "password": PASSWORD},
        "id": 1,
    }
    response = requests.post(ZABBIX_URL, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise Exception(f"Login failed: {data['error']}")
    return data["result"]

# --- GENERIC API CALL ---
def zabbix_api(method, params, token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }
    response = requests.post(ZABBIX_URL, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise Exception(f"API error: {data['error']}")
    return data["result"]

# --- AUTH ---
auth_token = zabbix_login()

# --- TIME RANGE ---
time_till = int(datetime.datetime.now().timestamp())
time_from = int((datetime.datetime.now() - datetime.timedelta(days=7)).timestamp())

# --- PDF SETUP ---
doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=A4)
styles = getSampleStyleSheet()
elements = []
elements.append(Paragraph("Zabbix CPU, Memory, and Disk Usage Report (Selected Groups)", styles['Title']))
elements.append(Paragraph("Period: Last 7 days", styles['Normal']))
elements.append(Spacer(1, 20))

for group in GROUPS:
    groupid = group["groupid"]
    groupname = group["name"]

    elements.append(Paragraph(f"Host Group: {groupname}", styles['Heading1']))
    elements.append(Spacer(1, 12))

    hosts = zabbix_api("host.get", {
        "groupids": groupid,
        "output": ["hostid", "host"]
    }, auth_token)

    if not hosts:
        elements.append(Paragraph("⚠️ No hosts found in this group.", styles['Normal']))
        elements.append(PageBreak())
        continue

    # Collect data per metric
    results = {metric: {} for metric in ITEM_KEYS.keys()}

    for host in hosts:
        hostid = host["hostid"]
        hostname = host["host"]

        for metric_name, item_key in ITEM_KEYS.items():
            items = zabbix_api("item.get", {
                "hostids": hostid,
                "search": {"key_": item_key},
                "output": ["itemid", "name", "key_"]
            }, auth_token)

            if not items:
                continue

            itemid = items[0]["itemid"]

            history = zabbix_api("history.get", {
                "output": "extend",
                "history": 0,  # float
                "itemids": itemid,
                "time_from": time_from,
                "time_till": time_till,
                "sortfield": "clock",
                "sortorder": "ASC"
            }, auth_token)

            daily_data = defaultdict(list)
            for h in history:
                ts = datetime.datetime.fromtimestamp(int(h["clock"]))
                day = ts.strftime("%Y-%m-%d")
                daily_data[day].append(float(h["value"]))

            daily_stats = {}
            for day, vals in daily_data.items():
                if vals:
                    daily_stats[day] = {
                        "min": min(vals),
                        "max": max(vals),
                        "avg": sum(vals) / len(vals),
                        "last": vals[-1]
                    }

            results[metric_name][hostname] = daily_stats

    # --- CHARTS ---
    # for metric_name, hosts_data in results.items():
    #     if not hosts_data:
    #         continue

    #     chart_file = os.path.join(CHART_DIR, f"group_{groupid}_{metric_name.replace(' ', '_')}.png")
    #     plt.figure(figsize=(10, 6))
    #     for host, days in hosts_data.items():
    #         x = sorted(days.keys())
    #         y = [days[d]["avg"] for d in x]
    #         plt.plot(x, y, marker="o", label=host)

    #     plt.title(f"{groupname} - Daily Avg {metric_name}")
    #     plt.xlabel("Date")
    #     plt.ylabel(metric_name)
    #     plt.xticks(rotation=45)
    #     plt.grid(True)
    #     plt.tight_layout()
    #     plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
    #     plt.savefig(chart_file,bbox_inches='tight')
    #     plt.close()

    #     elements.append(Image(chart_file, width=500, height=300))
    #     elements.append(Spacer(1, 12))

    # --- TABLES ---
    # for metric_name, hosts_data in results.items():
    #     for host, days in hosts_data.items():
    #         elements.append(Paragraph(f"Host: {host} - {metric_name}", styles['Heading2']))

    #         data = [["Date", "Min", "Max", "Avg", "Last"]]
    #         for day, stats in sorted(days.items()):
    #             data.append([
    #                 day,
    #                 f"{stats['min']:.2f}",
    #                 f"{stats['max']:.2f}",
    #                 f"{stats['avg']:.2f}",
    #                 f"{stats['last']:.2f}",
    #             ])

    #         table = Table(data, hAlign="LEFT")
    #         table.setStyle(TableStyle([
    #             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    #             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    #             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    #         ]))
    #         elements.append(table)
    #         elements.append(Spacer(1, 12))

    # --- TOP 3 TABLES ---
    # for metric_name, hosts_data in results.items():
    #     if metric_name not in ["CPU Usage (%)", "Memory Usage (%)"]:
    #         continue  # only CPU & Memory

    #     # Compute weekly max per host
    #     host_max = []
    #     for host, days in hosts_data.items():
    #         all_max = [stats["max"] for stats in days.values()]
    #         if all_max:
    #             weekly_max = max(all_max)
    #             host_max.append((host, weekly_max))

    #     # Sort & take top 3
    #     top_hosts = sorted(host_max, key=lambda x: x[1], reverse=True)[:3]

    #     if not top_hosts:
    #         continue

    #     # Table header
    #     elements.append(Paragraph(f"Top 3 Hosts by Weekly Max {metric_name}", styles['Heading2']))
    #     data = [["Host", f"Max {metric_name}"]]

    #     # Add rows
    #     for host, max_val in top_hosts:
    #         data.append([host, f"{max_val:.2f}"])

    #     # Format table
    #     table = Table(data, hAlign="LEFT")
    #     table.setStyle(TableStyle([
    #         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    #         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    #         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    #     ]))
    #     elements.append(table)
    #     elements.append(Spacer(1, 12))

    # --- CHARTS + TOP 3 TABLES ---
    for metric_name, hosts_data in results.items():
        if not hosts_data:
            continue

        # --- Chart ---
        chart_file = os.path.join(CHART_DIR, f"group_{groupid}_{metric_name.replace(' ', '_')}.png")
        plt.figure(figsize=(10, 6))
        for host, days in hosts_data.items():
            x = sorted(days.keys())
            y = [days[d]["avg"] for d in x]
            plt.plot(x, y, marker="o", label=host)

        plt.title(f"{groupname} - Daily Avg {metric_name}")
        plt.xlabel("Date")
        plt.ylabel(metric_name)
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.savefig(chart_file, bbox_inches='tight')
        plt.close()

        elements.append(Image(chart_file, width=500, height=300))
        elements.append(Spacer(1, 12))

        # --- Top 3 Table only for CPU & Memory ---
        if metric_name in ["CPU Usage (%)", "Memory Usage (%)"]:
            host_max = []
            for host, days in hosts_data.items():
                all_max = [stats["max"] for stats in days.values()]
                if all_max:
                    weekly_max = max(all_max)
                    host_max.append((host, weekly_max))

            top_hosts = sorted(host_max, key=lambda x: x[1], reverse=True)[:3]

            if top_hosts:
                elements.append(Paragraph(f"Top 3 Hosts by Weekly Max {metric_name}", styles['Heading6']))
                data = [["Host", f"Max {metric_name}"]]
                for host, max_val in top_hosts:
                    data.append([host, f"{max_val:.2f}"])

                table = Table(data, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 20))


        elements.append(PageBreak())

# --- BUILD PDF ---
doc.build(elements)
print(f"✅ PDF report generated: {OUTPUT_PDF}")
