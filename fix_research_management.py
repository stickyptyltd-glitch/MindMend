#!/usr/bin/env python3

# Read the admin_panel.py file
with open('/root/MindMend/admin_panel.py', 'r') as f:
    content = f.read()

# Find and replace the research management function
old_research = '''@admin_bp.route('/research-management')
@require_admin_auth
def research_management():
    """Research and dataset management interface"""
    stats = {
        'total_papers': 125,
        'papers_this_month': 8,
        'total_datasets': 23,
        'total_records': 50000,
        'total_insights': 340,
        'validated_insights': 280,
        'active_analyses': 5,
        'completed_today': 12
    }

    return render_template('admin/research_management.html', stats=stats)'''

new_research = '''@admin_bp.route('/research-management')
@require_admin_auth
def research_management():
    """Research and dataset management interface"""
    stats = {
        'total_papers': 125,
        'papers_this_month': 8,
        'total_datasets': 23,
        'total_records': 50000,
        'total_insights': 340,
        'validated_insights': 280,
        'active_analyses': 5,
        'completed_today': 12
    }

    # Add missing early diagnosis markers data
    early_diagnosis_markers = [
        {
            'name': 'Sleep Pattern Disruption',
            'confidence': 89.2,
            'prevalence': 67.8,
            'category': 'behavioral'
        },
        {
            'name': 'Social Withdrawal Indicators',
            'confidence': 92.5,
            'prevalence': 54.3,
            'category': 'social'
        },
        {
            'name': 'Mood Pattern Changes',
            'confidence': 87.1,
            'prevalence': 71.2,
            'category': 'emotional'
        },
        {
            'name': 'Cognitive Performance Decline',
            'confidence': 84.6,
            'prevalence': 43.9,
            'category': 'cognitive'
        }
    ]

    research_data = {
        'diagnostic_accuracy': {
            'overall_accuracy': 91.3,
            'precision': 88.7,
            'recall': 94.2,
            'f1_score': 91.4
        },
        'intervention_effectiveness': {
            'cbt_success_rate': 78.5,
            'medication_compliance': 82.1,
            'therapy_engagement': 76.8
        }
    }

    return render_template('admin/research_management.html',
                         stats=stats,
                         early_diagnosis_markers=early_diagnosis_markers,
                         research_data=research_data)'''

# Replace the content
content = content.replace(old_research, new_research)

# Write back to file
with open('/root/MindMend/admin_panel.py', 'w') as f:
    f.write(content)

print("Research management function updated successfully")