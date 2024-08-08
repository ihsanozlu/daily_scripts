marker=""
total=0

while true; do
    output=$(az storage blob list \
        --container-name your-container-name \
        --account-key container-account-key \
        --account-name account-name \
        --query "[*].[properties.contentLength]" \
        --output tsv \
        --marker "$marker"
        )
    
    if [ -z "$output" ]; then
        break
    fi
    
    sum=$(echo "$output" | awk '{ sum += $1 } END { print sum }')
    total=$(($total + $sum))
    marker=$(echo "$output" | tail -n1)
done

echo "Total content length: $total"

