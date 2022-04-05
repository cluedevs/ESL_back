echo "read api artifacts bucket ... "

API_ARTIFACTS_BUCKET=$(cat parameters-dev.json | jq -c '.[] | select(.ParameterKey | contains("artifactsBucket"))' | jq -r ".ParameterValue")
echo $API_ARTIFACTS_BUCKET

echo "Copying openapi definition to ${API_ARTIFACTS_BUCKET}..."
aws s3 cp ./api/api-gateway-openapi.yaml s3://${API_ARTIFACTS_BUCKET}/

# Install dependencies
sam build

sam package --template-file ./.aws-sam/build/template.yaml --s3-bucket rental-car-artifacts --s3-prefix rental-car --output-template-file out/template.yaml

aws cloudformation deploy --stack-name rental-car-api-stack-dev --template-file out/template.yaml \
                --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM --parameter-overrides file://parameters-dev.json 