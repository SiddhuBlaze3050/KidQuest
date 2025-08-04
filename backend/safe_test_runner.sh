#!/bin/bash
# safe_test_runner.sh - Safely run tests while preserving production database

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛡️ Safe Test Runner - Preserving Production Database${NC}"

# Step 1: Stop Flask server
echo -e "${YELLOW}📴 Stopping Flask server...${NC}"
pkill -f "python.*app.py" > /dev/null 2>&1 || true
sleep 2

# Step 2: Backup production database
DB_PATH="instance/app.db"
BACKUP_PATH="instance/app.db.backup.$(date +%Y%m%d_%H%M%S)"

if [ -f "$DB_PATH" ]; then
    echo -e "${YELLOW}💾 Backing up production database...${NC}"
    cp "$DB_PATH" "$BACKUP_PATH"
    echo -e "${GREEN}✅ Database backed up to: $BACKUP_PATH${NC}"
else
    echo -e "${RED}⚠️ No production database found${NC}"
fi

# Step 3: Run tests
echo -e "${YELLOW}🧪 Running tests...${NC}"
pytest test_files/test_task_tracker.py test_files/test_health_tracker.py -v

TEST_RESULT=$?

# Step 4: Restore production database
if [ -f "$BACKUP_PATH" ]; then
    echo -e "${YELLOW}🔄 Restoring production database...${NC}"
    cp "$BACKUP_PATH" "$DB_PATH"
    echo -e "${GREEN}✅ Production database restored${NC}"
    
    # Clean up backup (optional - comment out to keep backups)
    # rm "$BACKUP_PATH"
fi

# Step 5: Show results
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Production database preserved.${NC}"
else
    echo -e "${RED}❌ Some tests failed. Check output above.${NC}"
fi

echo -e "${YELLOW}📊 Current database status:${NC}"
python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('instance/app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM user ORDER BY id;')
    users = cursor.fetchall()
    print('Users in database:')
    for user in users:
        print(f'  ID: {user[0]}, Username: {user[1]}, Role: {user[2]}')
    print(f'Total users: {len(users)}')
    conn.close()
except Exception as e:
    print(f'Error checking database: {e}')
"

exit $TEST_RESULT
