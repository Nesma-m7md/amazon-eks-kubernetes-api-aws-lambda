#!/bin/bash
if ! hash aws 2>/dev/null; then
    echo "This script requires the AWS cli installed"
    exit 2
fi

# Ask the user if they are using multiple AWS profiles
read -p "Are you using multiple AWS profiles? (y/N): " use_profiles
use_profiles=${use_profiles,,}  # Convert to lowercase


if [[ "$use_profiles" == "y" || "$use_profiles" == "yes" ]]; then
    # User uses profiles
    if [ -z "$AWS_PROFILE" ]; then
        echo "Available profiles:"
        aws configure list-profiles
        read -p "Enter your AWS CLI profile name: " PROFILE
    else
        PROFILE="$AWS_PROFILE"
    fi
else
    # User does not use profiles — rely on default credentials
    echo "Proceeding using default AWS credentials..."
    PROFILE=""  # No need to pass --profile
fi


BUCKET_ID=$(dd if=/dev/random bs=8 count=1 2>/dev/null | od -An -tx1 | tr -d ' \t\n')
BUCKET_NAME=lambda-artifacts-$BUCKET_ID
echo $BUCKET_NAME > bucket-name.txt
aws s3 mb s3://$BUCKET_NAME

echo "Enter your cluster name: "
read CLUSTER_NAME
echo $CLUSTER_NAME > cluster-name.txt
