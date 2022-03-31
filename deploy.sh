echo "Copying openapi definition to ${S3_BUCKET}..."
aws s3 cp ./openapi/api-gateway-openapi.yaml s3://${S3_BUCKET}/

sam package --template-file ./template.yaml --s3-bucket sdlf-cfn-artifacts-us-west-2-397853315599 --s3-prefix research --output-template-file out/template.yaml

aws cloudformation deploy --stack-name rental-car-api-stack-dev --template-file out/template.yaml \
                --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM --parameter-overrides file://parameters-dev.json 