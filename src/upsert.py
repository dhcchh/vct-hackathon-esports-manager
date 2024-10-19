import boto3
import os

def upload_files_to_s3(bucket_name, folder_path='.'):
    # Create an S3 client
    s3_client = boto3.client('s3')
    
    # Get all files from the root folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(f)]
    
    for file in files:
        # The S3 key will be the file name as-is
        s3_key = file
        
        # Upload file to S3
        print(f"Uploading {file} to s3://{bucket_name}/{s3_key}")
        s3_client.upload_file(file, bucket_name, s3_key)

    print("All files uploaded successfully!")

# Example usage:
# bucket_name = 'our-bucket-name'      # Placeholder used here for our bucket name
# upload_files_to_s3(bucket_name)\