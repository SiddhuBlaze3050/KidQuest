from datetime import datetime, timezone
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import db, Notification, User, ParentChild, HealthStreak, LoginStreak
import json

class NotificationService:
    """Service class for creating and managing notifications"""
    
    # Notification type templates
    CHILD_TEMPLATES = {
        'achievement': {
            'icon': '🏆',
            'template': '🏆 {title}! You earned {stars} stars!',
            'priority': 'normal'
        },
        'level_up': {
            'icon': '🌟',
            'template': '🌟 Level Up! Welcome to Level {level} - {title}!',
            'priority': 'high'
        },
        'health': {
            'icon': '💪',
            'template': '💪 Amazing! {streak_days} day health streak!',
            'priority': 'normal'
        },
        'learning': {
            'icon': '📚',
            'template': '📚 Fantastic! You completed {module_name}!',
            'priority': 'normal'
        },
        'financial': {
            'icon': '💰',
            'template': '💰 Great job! Your savings goal is {progress}% complete!',
            'priority': 'normal'
        },
        'task_complete': {
            'icon': '✅',
            'template': '✅ Task completed: {task_name}!',
            'priority': 'low'
        },
        'streak_milestone': {
            'icon': '🔥',
            'template': '🔥 Incredible! {streak_days} day streak - you\'re on fire!',
            'priority': 'high'
        },
        'system': {
            'icon': '✨',
            'template': '✨ {message}',
            'priority': 'low'
        }
    }
    
    @staticmethod
    def create_notification(user_id, content, notification_type='general', 
                          priority='normal', action_url=None, related_user_id=None, extra_data=None):
        """Create a new notification"""
        try:
            print(f"📝 Starting notification creation: user_id={user_id}, type={notification_type}, content='{content[:50]}...'")
            
            # Use standard timestamp - models.py was updated to use datetime.utcnow
            current_time = datetime.utcnow()
            
            notification = Notification(
                user_id=user_id,
                content=content,
                notification_type=notification_type,
                priority=priority,
                action_url=action_url,
                related_user_id=related_user_id,
                extra_data=extra_data
                # timestamp will be set automatically by the model default
            )
            db.session.add(notification)
            db.session.commit()
            print(f"✅ Notification created successfully with ID: {notification.id}, timestamp: {notification.timestamp.isoformat()}")
            print(f"📋 Notification details: type={notification.notification_type}, priority={notification.priority}")
            return notification
        except Exception as e:
            print(f"❌ Error creating notification: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def notify_achievement(user_id, achievement_name, stars_earned=0):
        """Notify child of new achievement"""
        template = NotificationService.CHILD_TEMPLATES['achievement']
        content = template['template'].format(
            title=achievement_name,
            stars=stars_earned
        )
        
        return NotificationService.create_notification(
            user_id=user_id,
            content=content,
            notification_type='achievement',
            priority=template['priority'],
            extra_data={
                'achievement': achievement_name,
                'stars': stars_earned,
                'icon': template['icon']
            }
        )
    
    @staticmethod
    def notify_level_up(user_id, new_level, level_title):
        """Notify child of level up"""
        template = NotificationService.CHILD_TEMPLATES['level_up']
        content = template['template'].format(
            level=new_level,
            title=level_title
        )
        
        return NotificationService.create_notification(
            user_id=user_id,
            content=content,
            notification_type='achievement',
            priority=template['priority'],
            extra_data={
                'level': new_level,
                'title': level_title,
                'icon': template['icon']
            }
        )
    
    @staticmethod
    def notify_health_streak(user_id, streak_days):
        """Notify child of health streak milestone"""
        template = NotificationService.CHILD_TEMPLATES['health']
        
        # Use special template for milestone streaks
        if streak_days >= 7:
            template = NotificationService.CHILD_TEMPLATES['streak_milestone']
        
        content = template['template'].format(streak_days=streak_days)
        
        return NotificationService.create_notification(
            user_id=user_id,
            content=content,
            notification_type='health',
            priority=template['priority'],
            extra_data={
                'streak_days': streak_days,
                'icon': template['icon']
            }
        )
    
    @staticmethod
    def notify_module_completion(user_id, module_name, progress_percentage=100):
        """Notify child of learning module completion"""
        template = NotificationService.CHILD_TEMPLATES['learning']
        content = template['template'].format(module_name=module_name)
        
        return NotificationService.create_notification(
            user_id=user_id,
            content=content,
            notification_type='learning',
            priority=template['priority'],
            action_url=f'/learning/{module_name.lower().replace(" ", "-")}',
            extra_data={
                'module': module_name,
                'progress': progress_percentage,
                'icon': template['icon']
            }
        )
    
    @staticmethod
    def notify_savings_milestone(user_id, goal_name, progress_percentage):
        """Notify child of savings goal progress"""
        template = NotificationService.CHILD_TEMPLATES['financial']
        content = template['template'].format(progress=progress_percentage)
        
        return NotificationService.create_notification(
            user_id=user_id,
            content=content,
            notification_type='financial',
            priority=template['priority'],
            action_url='/finance-tracker',
            extra_data={
                'goal': goal_name,
                'progress': progress_percentage,
                'icon': template['icon']
            }
        )
    
    @staticmethod
    def notify_task_completion(user_id, task_name):
        """Notify child of task completion"""
        template = NotificationService.CHILD_TEMPLATES['task_complete']
        content = template['template'].format(task_name=task_name)
        
        print(f"🔔 Creating task completion notification for user {user_id}: {content}")
        
        result = NotificationService.create_notification(
            user_id=user_id,
            content=content,
            notification_type='achievement',  # Changed from 'system' to 'achievement' for better filtering
            priority=template['priority'],
            extra_data={
                'task': task_name,
                'icon': template['icon']
            }
        )
        
        print(f"📝 Task completion notification creation result: {result}")
        return result
    
    @staticmethod
    def notify_welcome(user_id, username):
        """Send welcome notification to new users"""
        content = f"🌟 Welcome to your magical adventure world, {username}! Let's start learning and having fun!"
        
        return NotificationService.create_notification(
            user_id=user_id,
            content=content,
            notification_type='system',
            priority='normal',
            extra_data={
                'welcome': True,
                'icon': '🌟'
            }
        )
    
    @staticmethod
    def check_and_notify_streaks(user_id):
        """Check for various streaks and create notifications if milestones reached"""
        # Check health streak
        health_streak = HealthStreak.query.filter_by(user_id=user_id).first()
        if health_streak and health_streak.current_streak > 0:
            milestone_days = [3, 7, 14, 21, 30, 60, 90]
            if health_streak.current_streak in milestone_days:
                NotificationService.notify_health_streak(user_id, health_streak.current_streak)
        
        # Check login streak
        login_streak = LoginStreak.query.filter_by(user_id=user_id).first()
        if login_streak and login_streak.current_streak > 0:
            milestone_days = [5, 10, 20, 30, 50, 100]
            if login_streak.current_streak in milestone_days:
                content = f"🎯 Dedication pays off! {login_streak.current_streak} day login streak!"
                NotificationService.create_notification(
                    user_id=user_id,
                    content=content,
                    notification_type='achievement',
                    priority='normal',
                    extra_data={
                        'login_streak': login_streak.current_streak,
                        'icon': '🎯'
                    }
                ) 