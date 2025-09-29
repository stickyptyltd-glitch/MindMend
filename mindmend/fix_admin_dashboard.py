#!/usr/bin/env python3

# Read the admin_panel.py file
with open('/root/MindMend/admin_panel.py', 'r') as f:
    content = f.read()

# Find the dashboard function and replace the dashboard_data
old_dashboard_data = '''    dashboard_data = {
        'system_stats': {
            'total_users': 1247,
            'active_sessions': 45,
            'total_counselors': 23,
            'revenue_this_month': 45600,
            'platform_uptime': '99.9%'
        },
        'recent_activities': [
            {
                'action': 'User Registration',
                'details': 'New user signed up',
                'timestamp': datetime.utcnow() - timedelta(minutes=15),
                'type': 'user'
            },
            {
                'action': 'Payment Processed',
                'details': 'Premium subscription - $99 AUD',
                'timestamp': datetime.utcnow() - timedelta(hours=2),
                'type': 'payment'
            }
        ]
    }'''

new_dashboard_data = '''    dashboard_data = {
        'system_stats': {
            'total_users': 1247,
            'active_sessions': 45,
            'total_counselors': 23,
            'revenue_this_month': 45600,
            'platform_uptime': '99.9%'
        },
        'platform_config': {
            'platform_settings': {
                'version': '2.0.1'
            }
        },
        'alerts': [],  # No current alerts
        'recent_activities': [
            {
                'action': 'User Registration',
                'details': 'New user signed up',
                'timestamp': datetime.utcnow() - timedelta(minutes=15),
                'type': 'user'
            },
            {
                'action': 'Payment Processed',
                'details': 'Premium subscription - $99 AUD',
                'timestamp': datetime.utcnow() - timedelta(hours=2),
                'type': 'payment'
            }
        ]
    }'''

# Replace the content
content = content.replace(old_dashboard_data, new_dashboard_data)

# Write back to file
with open('/root/MindMend/admin_panel.py', 'w') as f:
    f.write(content)

print("Admin dashboard data structure fixed successfully")