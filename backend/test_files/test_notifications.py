#!/usr/bin/env python3
"""
Notification System Test Script
Tests the notification functionality between frontend and backend
"""

import requests
import pytest

# Mark this module as integration since it depends on a running backend server
pytestmark = pytest.mark.integration
import json
import sys

BASE_URL = "http://localhost:5000"

def test_notification_system():
    """Test the complete notification system"""
    print("🔔 Testing Notification System")
    print("=" * 50)
    
    # First, login to get a token
    print("\n1. Logging in to get authentication token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200 and response.json().get('success'):
            token = response.json().get('access_token')
            user_data = response.json().get('user')
            user_id = user_data['id']
            headers = {"Authorization": f"Bearer {token}"}
            print(f"   ✅ Login successful! User ID: {user_id}")
        else:
            print(f"   ❌ Login failed: {response.json()}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    # Test 2: Get notifications (initially should be empty or have some)
    print("\n2. Testing Get Notifications...")
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/{user_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Get notifications successful!")
            print(f"   📊 Found {len(data.get('notifications', []))} notifications")
            initial_notifications = data.get('notifications', [])
        else:
            print(f"   ❌ Get notifications failed: {response.json()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Get notifications error: {e}")
        return False
    
    # Test 3: Get notifications again to verify they exist
    print("\n3. Testing Get Notifications Again...")
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/{user_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            new_notifications = data.get('notifications', [])
            print(f"   ✅ Get notifications successful!")
            print(f"   📊 Found {len(new_notifications)} total notifications")
            
            # Show some notification details
            unread_count = len([n for n in new_notifications if not n['is_read']])
            print(f"   📋 Unread notifications: {unread_count}")
            
            if new_notifications:
                print(f"   📝 Latest notification: \"{new_notifications[0]['content'][:50]}...\"")
                
        else:
            print(f"   ❌ Get notifications failed after creation")
            
    except Exception as e:
        print(f"   ❌ Get notifications after creation error: {e}")
    
    # Test 5: Mark notifications as read
    print("\n5. Testing Mark Notifications As Read...")
    try:
        # Get unread notification IDs
        unread_notifications = [n for n in new_notifications if not n['is_read']]
        if unread_notifications:
            notification_ids = [n['id'] for n in unread_notifications[:2]]  # Mark first 2 as read
            
            response = requests.post(f"{BASE_URL}/api/notifications/mark-read", 
                                   json={"notification_ids": notification_ids}, 
                                   headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            
            if response.status_code == 200:
                print(f"   ✅ Marked {len(notification_ids)} notifications as read!")
            else:
                print(f"   ❌ Mark notifications as read failed")
        else:
            print(f"   ⚠️ No unread notifications to mark as read")
            
    except Exception as e:
        print(f"   ❌ Mark notifications as read error: {e}")
    
    # Test 6: Verify notifications are marked as read
    print("\n6. Testing Notification Read Status Update...")
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/{user_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            final_notifications = data.get('notifications', [])
            unread_count = len([n for n in final_notifications if not n['is_read']])
            read_count = len([n for n in final_notifications if n['is_read']])
            
            print(f"   ✅ Final notification status:")
            print(f"   📊 Total: {len(final_notifications)}, Unread: {unread_count}, Read: {read_count}")
            
        else:
            print(f"   ❌ Failed to verify read status")
            
    except Exception as e:
        print(f"   ❌ Verify read status error: {e}")
    
    # Test 7: Test unauthorized access
    print("\n7. Testing Unauthorized Access...")
    try:
        wrong_user_id = 999  # Assuming this doesn't match the logged-in user
        response = requests.get(f"{BASE_URL}/api/notifications/{wrong_user_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 403:
            print(f"   ✅ Properly rejected unauthorized access!")
        else:
            print(f"   ⚠️ Security check: should reject access to other user's notifications")
            
    except Exception as e:
        print(f"   ❌ Unauthorized access test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Notification System Test Complete!")
    return True

def test_notification_generation():
    """Test automatic notification generation on login"""
    print("\n\n🔔 Testing Automatic Notification Generation")
    print("=" * 50)
    
    # Login should trigger notification generation
    print("\n1. Testing notification generation on login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200 and response.json().get('success'):
            token = response.json().get('access_token')
            user_data = response.json().get('user')
            user_id = user_data['id']
            headers = {"Authorization": f"Bearer {token}"}
            print(f"   ✅ Login successful - notifications should be generated")
            
            # Check if notifications were generated
            response = requests.get(f"{BASE_URL}/api/notifications/{user_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('notifications', [])
                recent_notifications = [n for n in notifications if 'Welcome back' in n['content'] or 'stars' in n['content']]
                
                print(f"   📊 Total notifications: {len(notifications)}")
                print(f"   🔄 Recent auto-generated: {len(recent_notifications)}")
                
                if recent_notifications:
                    print(f"   ✅ Auto-generation working!")
                else:
                    print(f"   ⚠️ No auto-generated notifications found")
                    
        else:
            print(f"   ❌ Login failed")
            
    except Exception as e:
        print(f"   ❌ Auto-generation test error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Notification System Tests...")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/auth/login", timeout=5)
        print("✅ Backend is responding")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running! Please start the Flask backend first.")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️ Backend check failed: {e}")
    
    # Run tests
    test_notification_system()
    test_notification_generation()
    
    print("\n🏁 All notification tests completed!")
