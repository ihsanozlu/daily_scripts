#!/bin/bash

ORG_URL="https://dev.azure.com/your_organization"
PROJECT="your_project"

# Get pipeline names that contain "master-CI" and exclude "model" and "entity"
pipelines=$(az pipelines list \
  --org "$ORG_URL" \
  --project "$PROJECT" \
  --query '[?contains(name, `master-CI`) && !contains(name, `model`) && !contains(name, `entity`)].name' \
  -o tsv)

echo "✅ Found pipelines to trigger:"
echo "$pipelines"
echo "------------------------------------"

triggered_count=0
failed_count=0

for pipelineName in $pipelines; do
  echo " Triggering pipeline: $pipelineName"

  # Try to run the pipeline
  if az pipelines run \
    --name "$pipelineName" \
    --branch "master" \
    --org "$ORG_URL" \
    --project "$PROJECT"; then
      ((triggered_count++))
      echo "✅ Successfully triggered: $pipelineName"
  else
      ((failed_count++))
      echo "❌ Failed to trigger: $pipelineName"
  fi

  echo "------------------------------------"
done

echo "🎯 Summary"
echo "✅ Pipelines triggered successfully: $triggered_count"
echo "❌ Pipelines failed to trigger: $failed_count"
echo "📦 Total processed: $((triggered_count + failed_count))"
