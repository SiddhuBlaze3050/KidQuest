import requests
import json
import pytest
from datetime import datetime
import time

class TestAdminUserManagement:
    """
    Comprehensive test suite for Admin User Management CRUD operations
    
    This test suite covers:
    1. Admin authentication a                    print("🔒 Testing admin creation (should be blocked)")
        response = self.session.post(f"{self.base_url}/api/admin/users", json=admin_data)
        print(f"📊 Status Code: {response.status_code}")
        
        # Admin creation should be blocked (expecting 403 Forbidden or 400 Bad Request)
        assert response.status_code in [400, 403], f"Admin creation should be blocked, got {response.status_code}: {response.text}"
        print("✅ Admin creation properly blocked")esting admin creation (should be blocked)")
        response = self.session.post(f"{self.base_url}/api/admin/users", json=admin_data)
        print(f"📊 Status Code: {response.status_code}")
        
        # Admin creation should be blocked (expecting 403 Forbidden or 400 Bad Request)
        assert response.status_code in [400, 403], f"Admin creation should be blocked, got {response.status_code}: {response.text}"
        print("✅ Admin creation properly blocked")esting admin creation (should be blocked)")
        response = self.session.post(f"{self.base_url}/api/admin/users", json=admin_data)
        print(f"📊 Status Code: {response.status_code}")
        
        # Admin creation should be blocked (expecting 403 Forbidden or 400 Bad Request)
        assert response.status_code in [400, 403], f"Admin creation should be blocked, got {response.status_code}: {response.text}"
        print("✅ Admin creation properly blocked")ion
    2. User creation for different roles (parent, child, teacher)
    3. User retrieval and listing
    4. User updates and modifications
    5. User deletion and cleanup
    6. Security and validation testing
    """
    
    def setup_class(self):
        """Setup class-level variables that are shared across all tests"""
        self.base_url = "http://localhost:5000"
        
        # Test data templates for different user types (excluding admin)
        self.user_templates = {
            'parent': {
                'username': 'test_parent_{}',
                'email': 'parent{}@example.com',
                'password': 'ParentPass123!',
                'role': 'parent'
            },
            'child': {
                'username': 'test_child_{}',
                'email': 'child{}@example.com',
                'password': 'ChildPass123!',
                'role': 'child'
            },
            'teacher': {
                'username': 'test_teacher_{}',
                'email': 'teacher{}@example.com',
                'password': 'TeacherPass123!',
                'role': 'teacher'
            }
        }
    
    def setup_method(self, method):
        """Setup method-level variables that need to be fresh for each test"""
        self.admin_token = None
        self.test_users = []
        self.session = requests.Session()
        
        # Setup admin authentication for each test
        self.setup_admin_auth()
    
    def teardown_method(self, method):
        """Clean up after each test method"""
        # Clean up any test users created during the test
        if hasattr(self, 'test_users') and self.test_users:
            self.cleanup_test_users()
        
        # Close the session
        if hasattr(self, 'session'):
            self.session.close()
    
    def setup_admin_auth(self):
        """Setup admin authentication for testing"""
        try:
            # Login as admin
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['access_token']
                self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                print("✅ Admin authentication successful")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
            return False
    
    def test_admin_dashboard_stats(self):
        """Test admin dashboard statistics endpoint"""
        print("\n" + "="*60)
        print("🧪 TESTING: Admin Dashboard Statistics")
        print("="*60)
        
        response = self.session.get(f"{self.base_url}/api/admin/dashboard-stats")
        
        print(f"📡 Request: GET /api/admin/dashboard-stats")
        print(f"📊 Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert 'total_users' in data, "total_users missing from response"
        assert 'admin_count' in data, "admin_count missing from response"
        assert isinstance(data['total_users'], int), "total_users should be an integer"
        
        print("✅ Dashboard stats retrieved successfully")
        print(f"📈 Total Users: {data.get('total_users', 'N/A')}")
        print(f"👥 Admin Count: {data.get('admin_count', 'N/A')}")
        print(f"👨‍👩‍👧‍👦 Parent Count: {data.get('parent_count', 'N/A')}")
        print(f"👶 Child Count: {data.get('child_count', 'N/A')}")
        print(f"👨‍🏫 Teacher Count: {data.get('teacher_count', 'N/A')}")
        print(f"🟢 Active Today: {data.get('active_today', 'N/A')}")
    
    def create_user_helper(self, user_type, user_id=None):
        """Helper method for user creation (not a direct test)"""
        print(f"\n🧪 TESTING: Create {user_type.upper()} User")
        print("-" * 40)
        
        if user_id is None:
            user_id = int(time.time() * 1000) % 10000  # Unique ID
        
        user_data = self.user_templates[user_type].copy()
        user_data['username'] = user_data['username'].format(user_id)
        user_data['email'] = user_data['email'].format(user_id)
        
        try:
            response = self.session.post(f"{self.base_url}/api/admin/users", json=user_data)
            
            print(f"📡 Request: POST /api/admin/users")
            print(f"📋 User Data: {json.dumps(user_data, indent=2)}")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                created_user = data['user']
                print(f"✅ {user_type.capitalize()} user created successfully")
                print(f"🆔 User ID: {created_user['id']}")
                print(f"👤 Username: {created_user['username']}")
                print(f"📧 Email: {created_user['email']}")
                print(f"🏷️ Role: {created_user['role']}")
                
                # Store for cleanup
                self.test_users.append({
                    'id': created_user['id'],
                    'username': created_user['username'],
                    'role': user_type,
                    'original_data': user_data
                })
                
                return created_user
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                print(f"❌ Failed to create {user_type} user: {error_data}")
                return None
                
        except Exception as e:
            print(f"❌ User creation error: {str(e)}")
            return None
    
    def test_get_all_users(self):
        """Test retrieving all users"""
        print(f"\n🧪 TESTING: Get All Users")
        print("-" * 40)
        
        response = self.session.get(f"{self.base_url}/api/admin/users")
        
        print(f"📡 Request: GET /api/admin/users")
        print(f"📊 Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Failed to get users: {response.text}"
        
        data = response.json()
        users = data['users']
        print(f"✅ Retrieved {len(users)} users successfully")
        
        # Count users by role
        role_counts = {}
        for user in users:
            role = user['role']
            role_counts[role] = role_counts.get(role, 0) + 1
        
        print("📊 User Distribution:")
        for role, count in role_counts.items():
            print(f"   {role.capitalize()}: {count}")
        
        assert len(users) > 0, "Expected at least one user in the system"
        assert 'users' in data, "users key missing from response"
    
    def update_user_helper(self, user_id, updates):
        """Helper method for user update operations (not a direct test)"""
        print(f"\n🧪 TESTING: Update User {user_id}")
        print("-" * 40)
        
        try:
            response = self.session.put(f"{self.base_url}/api/admin/users/{user_id}", json=updates)
            
            print(f"📡 Request: PUT /api/admin/users/{user_id}")
            print(f"📋 Update Data: {json.dumps(updates, indent=2)}")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                updated_user = data['user']
                print(f"✅ User {user_id} updated successfully")
                print(f"👤 Username: {updated_user['username']}")
                print(f"📧 Email: {updated_user['email']}")
                print(f"🏷️ Role: {updated_user['role']}")
                return updated_user
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                print(f"❌ Failed to update user: {error_data}")
                return None
                
        except Exception as e:
            print(f"❌ User update error: {str(e)}")
            return None
    
    def delete_user_helper(self, user_id):
        """Helper method for user deletion (not a direct test)"""
        print(f"\n🧪 TESTING: Delete User {user_id}")
        print("-" * 40)
        
        try:
            response = self.session.delete(f"{self.base_url}/api/admin/users/{user_id}")
            
            print(f"📡 Request: DELETE /api/admin/users/{user_id}")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ User {user_id} deleted successfully")
                print(f"📝 Message: {data.get('message', 'User deleted')}")
                return True
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                print(f"❌ Failed to delete user: {error_data}")
                return False
                
        except Exception as e:
            print(f"❌ User deletion error: {str(e)}")
            return False
    
    def test_security_validations(self):
        """Test security validations and edge cases"""
        print(f"\n🧪 TESTING: Security Validations")
        print("-" * 40)
        
        # Test that admin creation is blocked
        unique_id = int(time.time() * 1000) % 10000
        admin_data = {
            'username': f'test_admin_{unique_id}',
            'email': f'admin{unique_id}@example.com',
            'password': 'AdminPass123!',
            'role': 'admin'
        }
        
        print("🔒 Testing admin creation (should be blocked)")
        response = self.session.post(f"{self.base_url}/api/admin/users", json=admin_data)
        print(f"� Status Code: {response.status_code}")
        
        # Admin creation should be blocked (expecting 403 Forbidden or 400 Bad Request)
        assert response.status_code in [400, 403], f"Admin creation should be blocked, got {response.status_code}: {response.text}"
        print("✅ Admin creation properly blocked")
    
    def test_duplicate_user_validation(self):
        """Test duplicate username/email validation"""
        print(f"\n🧪 TESTING: Duplicate User Validation")
        print("-" * 40)
        
        # Create a user first
        unique_id = int(time.time() * 1000) % 10000
        original_user = self.create_user_helper('parent', unique_id)
        
        assert original_user is not None, "Failed to create original user for duplicate test"
        
        # Try to create user with same username
        duplicate_username_data = {
            'username': original_user['username'],
            'email': f'different{unique_id}@example.com',
            'password': 'Password123!',
            'role': 'child'
        }
        
        print(f"\n🔒 Testing duplicate username")
        response = self.session.post(f"{self.base_url}/api/admin/users", json=duplicate_username_data)
        print(f"📊 Status Code: {response.status_code}")
        
        assert response.status_code == 409, f"Expected 409 for duplicate username, got {response.status_code}"
        print("✅ Duplicate username validation passed")
        
        # Try to create user with same email
        duplicate_email_data = {
            'username': f'different_user_{unique_id}',
            'email': original_user['email'],
            'password': 'Password123!',
            'role': 'teacher'
        }
        
        print(f"\n🔒 Testing duplicate email")
        response = self.session.post(f"{self.base_url}/api/admin/users", json=duplicate_email_data)
        print(f"📊 Status Code: {response.status_code}")
        
        assert response.status_code == 409, f"Expected 409 for duplicate email, got {response.status_code}"
        print("✅ Duplicate email validation passed")
    
    def test_unauthorized_access(self):
        """Test unauthorized access attempts"""
        print(f"\n🧪 TESTING: Unauthorized Access")
        print("-" * 40)
        
        # Save current authorization header
        current_auth = self.session.headers.get('Authorization')
        
        # Remove authorization
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
        
        try:
            # Test GET users without auth
            response = self.session.get(f"{self.base_url}/api/admin/users")
            print(f"📡 GET /api/admin/users (no auth)")
            print(f"📊 Status Code: {response.status_code}")
            
            assert response.status_code == 401, f"Expected 401 for unauthorized GET, got {response.status_code}"
            print("✅ Unauthorized GET properly blocked")
            
            # Test POST user without auth
            test_data = {
                'username': 'unauthorized_test',
                'email': 'unauth@example.com',
                'password': 'Password123!',
                'role': 'parent'
            }
            
            response = self.session.post(f"{self.base_url}/api/admin/users", json=test_data)
            print(f"📡 POST /api/admin/users (no auth)")
            print(f"📊 Status Code: {response.status_code}")
            
            assert response.status_code == 401, f"Expected 401 for unauthorized POST, got {response.status_code}"
            print("✅ Unauthorized POST properly blocked")
            
        finally:
            # Restore authorization
            if current_auth:
                self.session.headers['Authorization'] = current_auth

    # Individual pytest test methods for CRUD operations
    def test_create_parent_user(self):
        """Test creating a parent user"""
        user = self.create_user_helper('parent')
        assert user is not None, "Failed to create parent user"
        assert user['role'] == 'parent', f"Expected role 'parent', got {user['role']}"

    def test_create_child_user(self):
        """Test creating a child user"""
        user = self.create_user_helper('child')
        assert user is not None, "Failed to create child user"
        assert user['role'] == 'child', f"Expected role 'child', got {user['role']}"

    def test_create_teacher_user(self):
        """Test creating a teacher user"""
        user = self.create_user_helper('teacher')
        assert user is not None, "Failed to create teacher user"
        assert user['role'] == 'teacher', f"Expected role 'teacher', got {user['role']}"

    def test_user_update_operations(self):
        """Test user update functionality"""
        # Create a user first
        user = self.create_user_helper('parent')
        assert user is not None, "Failed to create user for update test"
        
        # Update the user
        updates = {
            'username': f"{user['username']}_updated",
            'email': f"updated_{user['email']}"
        }
        updated_user = self.update_user_helper(user['id'], updates)
        assert updated_user is not None, "Failed to update user"
        assert updated_user['username'] == updates['username'], "Username not updated correctly"

    def test_user_deletion(self):
        """Test user deletion functionality"""
        # Create a user first
        user = self.create_user_helper('parent')
        assert user is not None, "Failed to create user for deletion test"
        
        # Delete the user
        result = self.delete_user_helper(user['id'])
        assert result is True, "Failed to delete user"
        
        # Remove from test_users list to avoid duplicate cleanup
        self.test_users = [u for u in self.test_users if u['id'] != user['id']]
    
    def cleanup_test_users(self):
        """Clean up all test users created during testing"""
        print(f"\n🧹 CLEANING UP: Test Users")
        print("-" * 40)
        
        cleanup_count = 0
        for user in self.test_users:
            if self.delete_user_helper(user['id']):
                cleanup_count += 1
        
        print(f"🧹 Cleaned up {cleanup_count}/{len(self.test_users)} test users")
        self.test_users.clear()
    
    def run_comprehensive_tests(self):
        """Run all admin user management tests - for backwards compatibility"""
        print("\n" + "="*80)
        print("🚀 STARTING COMPREHENSIVE ADMIN USER MANAGEMENT TESTS")
        print("="*80)
        
        start_time = datetime.now()
        test_results = []
        
        try:
            # Test 1: Dashboard Stats
            test_results.append(('Dashboard Stats', self.test_admin_dashboard_stats()))
            
            # Test 2: Create users of different types (excluding admin)
            parent_user = self.create_user_helper('parent')
            test_results.append(('Create Parent', parent_user is not None))
            
            child_user = self.create_user_helper('child')
            test_results.append(('Create Child', child_user is not None))
            
            teacher_user = self.create_user_helper('teacher')
            test_results.append(('Create Teacher', teacher_user is not None))
            
            # Test 3: Get all users
            all_users = self.test_get_all_users()
            test_results.append(('Get All Users', all_users is not None))
            
            # Test 4: Update user (if we have a created user)
            if parent_user:
                updates = {
                    'username': f"{parent_user['username']}_updated",
                    'email': f"updated_{parent_user['email']}"
                }
                updated_user = self.update_user_helper(parent_user['id'], updates)
                test_results.append(('Update User', updated_user is not None))
            
            # Test 5: Security validations (including admin creation blocking)
            test_results.append(('Security Validations', self.test_security_validations()))
            
            # Test 6: Duplicate validation
            test_results.append(('Duplicate Validation', self.test_duplicate_user_validation()))
            
            # Test 7: Unauthorized access
            test_results.append(('Unauthorized Access', self.test_unauthorized_access()))
            
        except Exception as e:
            print(f"❌ Test execution error: {str(e)}")
        
        finally:
            # Cleanup
            self.cleanup_test_users()
        
        # Generate test report
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "="*80)
        print("📊 TEST RESULTS SUMMARY")
        print("="*80)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} | {test_name}")
            if result:
                passed += 1
        
        print("-" * 80)
        print(f"📈 Overall Results: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
        print(f"⏱️ Total Duration: {duration.total_seconds():.2f} seconds")
        
        if passed == total:
            print("🎉 All tests passed! Admin user management is working correctly.")
        else:
            print("⚠️ Some tests failed. Please review the failed tests above.")
        
        return passed == total

# Pytest-compatible test runner and backwards compatibility
def run_legacy_comprehensive_tests():
    """Run comprehensive tests in legacy mode for backwards compatibility"""
    # Create a temporary instance for legacy testing
    class LegacyTestRunner:
        def __init__(self):
            self.base_url = "http://localhost:5000"
            self.admin_token = None
            self.test_users = []
            self.session = requests.Session()
            
            # Test data templates for different user types (excluding admin)
            self.user_templates = {
                'parent': {
                    'username': 'test_parent_{}',
                    'email': 'parent{}@example.com',
                    'password': 'ParentPass123!',
                    'role': 'parent'
                },
                'child': {
                    'username': 'test_child_{}',
                    'email': 'child{}@example.com',
                    'password': 'ChildPass123!',
                    'role': 'child'
                },
                'teacher': {
                    'username': 'test_teacher_{}',
                    'email': 'teacher{}@example.com',
                    'password': 'TeacherPass123!',
                    'role': 'teacher'
                }
            }
    
    # Mix in all the test methods from the main class
    for method_name in dir(TestAdminUserManagement):
        if not method_name.startswith('_') and callable(getattr(TestAdminUserManagement, method_name)):
            setattr(LegacyTestRunner, method_name, getattr(TestAdminUserManagement, method_name))
    
    tester = LegacyTestRunner()
    
    # Setup admin auth
    if not tester.setup_admin_auth():
        print("❌ Failed to authenticate as admin. Aborting tests.")
        assert False, "Failed to authenticate as admin"
    
    result = tester.run_comprehensive_tests()
    assert result, "Comprehensive tests failed"

# Main execution for backwards compatibility
if __name__ == "__main__":
    success = run_legacy_comprehensive_tests()
    if not success:
        exit(1)
    exit(0)