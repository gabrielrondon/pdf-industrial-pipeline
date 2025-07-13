#!/usr/bin/env python3
"""
S3 Connection Test Script
Run this to verify your S3 setup before configuring the main application
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
from datetime import datetime

def test_s3_connection():
    """Test S3 connection with your credentials"""
    
    print("🔍 Testing S3 Connection...")
    print("=" * 50)
    
    # Get credentials from environment or prompt
    bucket_name = input("Enter your S3 bucket name: ").strip()
    access_key = input("Enter AWS Access Key ID: ").strip()
    secret_key = input("Enter AWS Secret Access Key: ").strip()
    region = input("Enter AWS region (default: us-east-1): ").strip() or "us-east-1"
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        print(f"\n✅ S3 client created successfully")
        print(f"📍 Region: {region}")
        print(f"🪣 Bucket: {bucket_name}")
        
        # Test 1: Check if bucket exists and is accessible
        print(f"\n🔍 Test 1: Checking bucket access...")
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' is accessible")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ Bucket '{bucket_name}' not found")
                return False
            elif error_code == '403':
                print(f"❌ Access denied to bucket '{bucket_name}'")
                return False
            else:
                print(f"❌ Error accessing bucket: {e}")
                return False
        
        # Test 2: Try to upload a test file
        print(f"\n🔍 Test 2: Testing file upload...")
        test_content = f"PDF Pipeline S3 Test - {datetime.now().isoformat()}"
        test_key = "test-files/connection-test.txt"
        
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content.encode(),
                ContentType='text/plain'
            )
            print(f"✅ Test file uploaded successfully: {test_key}")
        except ClientError as e:
            print(f"❌ Upload failed: {e}")
            return False
        
        # Test 3: Try to download the test file
        print(f"\n🔍 Test 3: Testing file download...")
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
            downloaded_content = response['Body'].read().decode()
            if downloaded_content == test_content:
                print(f"✅ File downloaded and verified successfully")
            else:
                print(f"⚠️ Downloaded content doesn't match uploaded content")
        except ClientError as e:
            print(f"❌ Download failed: {e}")
            return False
        
        # Test 4: Clean up test file
        print(f"\n🔍 Test 4: Testing file deletion...")
        try:
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            print(f"✅ Test file deleted successfully")
        except ClientError as e:
            print(f"⚠️ Could not delete test file: {e}")
        
        # Success summary
        print(f"\n" + "=" * 50)
        print(f"🎉 S3 Connection Test PASSED!")
        print(f"\n📋 Configuration Summary:")
        print(f"   Bucket: {bucket_name}")
        print(f"   Region: {region}")
        print(f"   Access Key: {access_key[:8]}...")
        print(f"\n🚀 Ready to configure Railway environment variables:")
        print(f"   STORAGE_BACKEND=s3")
        print(f"   S3_BUCKET={bucket_name}")
        print(f"   AWS_ACCESS_KEY_ID={access_key}")
        print(f"   AWS_SECRET_ACCESS_KEY={secret_key}")
        print(f"   S3_REGION={region}")
        
        return True
        
    except NoCredentialsError:
        print(f"❌ No AWS credentials found")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_s3_connection()
    if success:
        print(f"\n✅ You're ready to enable S3 storage!")
    else:
        print(f"\n❌ S3 setup needs attention before proceeding")