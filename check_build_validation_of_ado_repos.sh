ORG="your_ado_org"
PROJECT="your_ado_project"
PAT="your_ado_pat"


AUTH=$(printf ":%s" "$PAT" | base64)
url_for_repositories="https://dev.azure.com/$ORG/$PROJECT/_apis/git/repositories?includeLinks=true&includeAllUrls=false&includeHidden=false&api-version=7.1"
url_for_policies="https://dev.azure.com/$ORG/$PROJECT/_apis/policy/configurations?api-version=7.1"

TARGET_BRANCH="refs/heads/development"

repos=$(curl -s \
	-H "Authorization: Basic $AUTH" \
	 "$url_for_repositories")

#echo "== Repositories Listing=="
#echo "$PROJECT repositories are :"
#echo "$repos" | jq -r '.value[] | "\(.name) \(.id)"'


echo "Checking Build Validation for branch: $TARGET_BRANCH"
echo "----------------------------------------------------"

policies=$(curl -s \
	-H "Authorization: Basic $AUTH" \
  	"$url_for_policies")

echo "$repos" | jq -r '.value[] | "\(.name) \(.id)"' |
while read repo_name repo_id; do

    has_build=$(echo "$policies" | jq -r \
        --arg repo "$repo_id" \
        --arg branch "$TARGET_BRANCH" \
        '
        .value[]
        | select(.type.displayName == "Build")
        | select(.settings.scope[]?
            | select(.repositoryId == $repo and .refName == $branch))
        | .id
        ')

    if [ -n "$has_build" ] && [ "$has_build" != "null" ]; then
        echo "[OK]       $repo_name → Build Validation enabled"
    else
        echo "[MISSING]  $repo_name → NO Build Validation"
    fi
done
