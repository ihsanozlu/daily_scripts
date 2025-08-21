
az acr repository list --name azerlottery --output tsv | wc -l
184 repository
Total Images: 20053
Totat Size 4.1 TB

----

total_images=0
az acr repository list --name azerlottery --output tsv | while read repo; do
  count=$(az acr manifest list-metadata -r azerlottery -n $repo -o tsv | wc -l)
  total_images=$((total_images + count))
  echo "Total Images: $total_images"
done
echo "Total Images: $total_images"


----

total_size=0
az acr repository list --name azerlottery --output tsv | while read repo; do
  latest_tag=$(az acr manifest list-metadata -r azerlottery -n $repo --query "[?tags[?=='latest']].tags[0]" --output tsv)
  
  if [ ! -z "$latest_tag" ]; then
    latest_size=$(az acr manifest list-metadata -r azerlottery -n $repo --query "[?tags[?=='latest']].imageSize" --output tsv)
    
    total_size=$((total_size + latest_size))
    
    echo "Repository: $repo, Latest Tag: $latest_tag, Size: $latest_size bytes"
  else
    echo "Repository: $repo does not have the 'latest' tag."
  fi
done

echo "Total Size of 'latest' Images: $total_size bytes"


----


total_size=0
az acr repository list --name azerlottery --output tsv | while read repo; do
  latest_tag=$(az acr manifest list-metadata -r azerlottery -n $repo --query "[?contains(tags, 'latest')].tags[0]" --output tsv)
  
  if [ ! -z "$latest_tag" ]; then
    latest_size=$(az acr manifest list-metadata -r azerlottery -n $repo --query "[?contains(tags, 'latest')].imageSize" --output tsv)
  
    total_size=$((total_size + latest_size))
    
    echo "Repository: $repo, Latest Tag: $latest_tag, Size: $latest_size bytes"
  else
    echo "Repository: $repo does not have the 'latest' tag."
  fi
done

echo "Total Size of 'latest' Images: $total_size bytes"


---


total_size=0
az acr repository list --name azerlottery --output tsv | while read repo; do
  latest_tag=$(az acr manifest list-metadata -r azerlottery -n $repo --query "[?contains(tags, 'latest')].tags[0]" --output tsv)
  
  if [ "$latest_tag" = "latest" ]; then
    latest_size=$(az acr manifest list-metadata -r azerlottery -n $repo --query "[?contains(tags, 'latest')].imageSize" --output tsv)
    
    total_size=$((total_size + latest_size))
    
    echo "Repository: $repo, Latest Tag: $latest_tag, Size: $latest_size bytes"
  else
    echo "Repository: $repo does not have the 'latest' tag."
  fi
done

echo "Total Size of 'latest' Images: $total_size bytes"


