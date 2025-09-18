#!/usr/bin/env python3

# Create Therapy & Community Template with tabbed interface

template_content = '''{% extends "admin/base.html" %}

{% block title %}Therapy & Community - Mind Mend Admin{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Header Section -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="h3 mb-0">
                        <i class="fas fa-heart me-2 text-danger"></i>
                        Therapy & Community Management
                    </h1>
                    <p class="text-muted mb-0">Groups, Tools & Treatment Plans Dashboard</p>
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-outline-danger btn-sm">
                        <i class="fas fa-download me-1"></i>Export Reports
                    </button>
                    <button class="btn btn-danger btn-sm">
                        <i class="fas fa-sync-alt me-1"></i>Refresh
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Overview Cards -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card bg-danger text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h4 class="mb-0">{{ data.overview_stats.active_groups }}</h4>
                            <p class="mb-0">Active Groups</p>
                        </div>
                        <div class="align-self-center">
                            <i class="fas fa-users fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-success text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h4 class="mb-0">{{ data.overview_stats.therapy_sessions_today }}</h4>
                            <p class="mb-0">Sessions Today</p>
                        </div>
                        <div class="align-self-center">
                            <i class="fas fa-heartbeat fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-info text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h4 class="mb-0">{{ data.overview_stats.active_plans }}</h4>
                            <p class="mb-0">Active Plans</p>
                        </div>
                        <div class="align-self-center">
                            <i class="fas fa-clipboard-list fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-warning text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h4 class="mb-0">{{ "%.1f"|format(data.overview_stats.wellbeing_score) }}</h4>
                            <p class="mb-0">Wellbeing Score</p>
                        </div>
                        <div class="align-self-center">
                            <i class="fas fa-smile fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Therapy & Community Alerts -->
    {% if data.therapy_alerts %}
    <div class="row mb-4">
        <div class="col-12">
            {% for alert in data.therapy_alerts %}
            <div class="alert alert-{{ 'warning' if alert.level == 'warning' else 'info' if alert.level == 'info' else 'success' }} alert-dismissible fade show">
                <i class="fas fa-{{ 'exclamation-triangle' if alert.level == 'warning' else 'info-circle' if alert.level == 'info' else 'check-circle' }} me-2"></i>
                {{ alert.message }}
                <a href="#" class="alert-link ms-2" onclick="switchTab('{{ alert.tab }}')">{{ alert.action }}</a>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <!-- Tabbed Interface -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <ul class="nav nav-tabs card-header-tabs" id="therapyTabs">
                        <li class="nav-item">
                            <a class="nav-link {{ 'active' if data.active_tab == 'groups' else '' }}"
                               href="?tab=groups" id="groups-tab">
                                <i class="fas fa-users me-2"></i>Social Groups
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link {{ 'active' if data.active_tab == 'tools' else '' }}"
                               href="?tab=tools" id="tools-tab">
                                <i class="fas fa-tools me-2"></i>Therapy Tools
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link {{ 'active' if data.active_tab == 'plans' else '' }}"
                               href="?tab=plans" id="plans-tab">
                                <i class="fas fa-clipboard-list me-2"></i>Treatment Plans
                            </a>
                        </li>
                    </ul>
                </div>
                <div class="card-body">
                    <div class="tab-content" id="therapyTabContent">

                        <!-- Social Groups Tab -->
                        <div class="tab-pane fade {{ 'show active' if data.active_tab == 'groups' else '' }}"
                             id="groups" role="tabpanel">
                            <div class="row">
                                <!-- Active Groups -->
                                <div class="col-md-8">
                                    <h5 class="mb-3">
                                        <i class="fas fa-users text-danger me-2"></i>Active Support Groups
                                    </h5>

                                    {% for group in data.groups_data.active_groups_list %}
                                    <div class="card mb-3">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between">
                                                <div>
                                                    <h6 class="card-title">{{ group.name }}</h6>
                                                    <div class="mb-2">
                                                        <span class="badge bg-{{ 'primary' if group.category == 'anxiety_support' else 'info' if group.category == 'depression_support' else 'success' if group.category == 'general_wellness' else 'danger' }}">
                                                            {{ group.category.replace('_', ' ').title() }}
                                                        </span>
                                                        <small class="text-muted ms-2">Moderator: {{ group.moderator }}</small>
                                                    </div>
                                                    <div class="row">
                                                        <div class="col-md-4">
                                                            <small class="text-muted">Total Members</small>
                                                            <div class="fw-bold">{{ group.members }}</div>
                                                        </div>
                                                        <div class="col-md-4">
                                                            <small class="text-muted">Active This Week</small>
                                                            <div class="fw-bold text-success">{{ group.active_members }}</div>
                                                        </div>
                                                        <div class="col-md-4">
                                                            <small class="text-muted">Sessions This Week</small>
                                                            <div class="fw-bold text-info">{{ group.sessions_this_week }}</div>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div class="text-end">
                                                    <div class="mb-2">
                                                        <div class="fw-bold text-{{ 'success' if group.engagement_score > 90 else 'warning' if group.engagement_score > 75 else 'danger' }}">
                                                            {{ group.engagement_score }}%
                                                        </div>
                                                        <small class="text-muted">Engagement</small>
                                                    </div>
                                                    <small class="text-muted">Last Activity: {{ group.last_activity.strftime('%H:%M') }}</small>
                                                </div>
                                            </div>
                                            <div class="mt-3">
                                                <button class="btn btn-sm btn-outline-primary">View Details</button>
                                                <button class="btn btn-sm btn-outline-secondary">Moderate</button>
                                                <button class="btn btn-sm btn-outline-info">Analytics</button>
                                            </div>
                                        </div>
                                    </div>
                                    {% endfor %}

                                    <!-- Peer Matching Section -->
                                    <div class="card mt-4">
                                        <div class="card-header">
                                            <h6 class="mb-0">
                                                <i class="fas fa-handshake me-2"></i>Peer Matching System
                                            </h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="row">
                                                <div class="col-md-3">
                                                    <small class="text-muted">Total Matches</small>
                                                    <div class="fw-bold text-primary">{{ "{:,}".format(data.groups_data.peer_matching.total_matches) }}</div>
                                                </div>
                                                <div class="col-md-3">
                                                    <small class="text-muted">Success Rate</small>
                                                    <div class="fw-bold text-success">{{ "%.1f"|format(data.groups_data.peer_matching.match_success_rate) }}%</div>
                                                </div>
                                                <div class="col-md-3">
                                                    <small class="text-muted">Compatibility Score</small>
                                                    <div class="fw-bold text-info">{{ "%.1f"|format(data.groups_data.peer_matching.avg_compatibility_score) }}</div>
                                                </div>
                                                <div class="col-md-3">
                                                    <small class="text-muted">Pending Matches</small>
                                                    <div class="fw-bold text-warning">{{ data.groups_data.peer_matching.pending_matches }}</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Community Metrics Sidebar -->
                                <div class="col-md-4">
                                    <h6 class="mb-3">Community Health</h6>
                                    <div class="card border-0 bg-light">
                                        <div class="card-body">
                                            <div class="mb-3">
                                                <small class="text-muted">Overall Wellbeing</small>
                                                <div class="fw-bold text-success">{{ "%.1f"|format(data.community_health.overall_wellbeing_score) }}/10</div>
                                            </div>
                                            <div class="mb-3">
                                                <small class="text-muted">Engagement Rate</small>
                                                <div class="progress mb-1" style="height: 6px;">
                                                    <div class="progress-bar bg-primary" style="width: {{ data.community_health.community_engagement_rate }}%"></div>
                                                </div>
                                                <small>{{ "%.1f"|format(data.community_health.community_engagement_rate) }}%</small>
                                            </div>
                                            <div class="mb-3">
                                                <small class="text-muted">Crisis Response Time</small>
                                                <div class="fw-bold text-info">{{ data.community_health.crisis_response_time }}</div>
                                            </div>
                                            <div class="mb-3">
                                                <small class="text-muted">Safety Incidents</small>
                                                <div class="fw-bold text-{{ 'success' if data.community_health.safety_incidents == 0 else 'danger' }}">
                                                    {{ data.community_health.safety_incidents }}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <h6 class="mt-4 mb-3">Group Categories</h6>
                                    {% for category, count in data.groups_data.group_categories.items() %}
                                    <div class="mb-2">
                                        <div class="d-flex justify-content-between">
                                            <span>{{ category.replace('_', ' ').title() }}</span>
                                            <span class="badge bg-danger">{{ count }}</span>
                                        </div>
                                    </div>
                                    {% endfor %}
                                </div>
                            </div>
                        </div>

                        <!-- Therapy Tools Tab -->
                        <div class="tab-pane fade {{ 'show active' if data.active_tab == 'tools' else '' }}"
                             id="tools" role="tabpanel">
                            <h5 class="mb-4">
                                <i class="fas fa-tools text-success me-2"></i>Therapeutic Tools & Technologies
                            </h5>

                            <!-- Tool Usage Overview -->
                            <div class="row mb-4">
                                <div class="col-md-4">
                                    <div class="card border-0 bg-light">
                                        <div class="card-body text-center">
                                            <h4 class="text-info">{{ data.tools_data.vr_sessions_today }}</h4>
                                            <small class="text-muted">VR Sessions Today</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card border-0 bg-light">
                                        <div class="card-body text-center">
                                            <h4 class="text-warning">{{ data.tools_data.biofeedback_sessions }}</h4>
                                            <small class="text-muted">Biofeedback Sessions</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card border-0 bg-light">
                                        <div class="card-body text-center">
                                            <h4 class="text-success">{{ data.tools_data.ai_therapy_sessions }}</h4>
                                            <small class="text-muted">AI Therapy Sessions</small>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <!-- VR Environments -->
                                <div class="col-md-6">
                                    <h6 class="mb-3">VR Therapy Environments</h6>
                                    {% for env in data.tools_data.vr_environments_list %}
                                    <div class="card mb-3">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between">
                                                <div>
                                                    <h6 class="card-title">{{ env.name }}</h6>
                                                    <div class="mb-2">
                                                        <span class="badge bg-{{ 'primary' if env.category == 'relaxation' else 'info' if env.category == 'mindfulness' else 'success' }}">
                                                            {{ env.category.title() }}
                                                        </span>
                                                        <span class="badge bg-{{ 'success' if env.difficulty_level == 'beginner' else 'warning' if env.difficulty_level == 'intermediate' else 'danger' }} ms-1">
                                                            {{ env.difficulty_level.title() }}
                                                        </span>
                                                    </div>
                                                    <small class="text-muted">{{ env.therapy_type.replace('_', ' ').title() }}</small>
                                                </div>
                                                <div class="text-end">
                                                    <div class="fw-bold text-success">{{ env.effectiveness_score }}%</div>
                                                    <small class="text-muted">Effectiveness</small>
                                                    <div class="mt-1">
                                                        <small class="text-muted">{{ env.sessions_today }} sessions today</small>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="mt-2">
                                                <div class="d-flex justify-content-between">
                                                    <small>Duration: {{ env.duration_avg }}</small>
                                                    <small>Rating: {{ env.user_rating }}/5 ⭐</small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    {% endfor %}
                                </div>

                                <!-- Biofeedback Exercises -->
                                <div class="col-md-6">
                                    <h6 class="mb-3">Biofeedback Exercises</h6>
                                    {% for exercise in data.tools_data.biofeedback_exercises %}
                                    <div class="card mb-3">
                                        <div class="card-body">
                                            <h6 class="card-title">{{ exercise.name }}</h6>
                                            <div class="mb-2">
                                                <span class="badge bg-info">{{ exercise.category.title() }}</span>
                                                <span class="badge bg-{{ 'success' if exercise.difficulty == 'beginner' else 'warning' if exercise.difficulty == 'intermediate' else 'danger' }} ms-1">
                                                    {{ exercise.difficulty.title() }}
                                                </span>
                                            </div>
                                            <div class="row">
                                                <div class="col-6">
                                                    <small class="text-muted">Target</small>
                                                    <div class="fw-bold">{{ exercise.target_condition.title() }}</div>
                                                </div>
                                                <div class="col-6">
                                                    <small class="text-muted">Sessions Today</small>
                                                    <div class="fw-bold text-primary">{{ exercise.sessions_today }}</div>
                                                </div>
                                            </div>
                                            <div class="mt-2">
                                                <small class="text-muted">Avg Improvement: </small>
                                                <span class="fw-bold text-success">{{ exercise.avg_improvement }}%</span>
                                                <div class="mt-1">
                                                    <small class="text-muted">Rating: {{ exercise.effectiveness_rating }}/5 ⭐</small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    {% endfor %}

                                    <!-- Tool Effectiveness Summary -->
                                    <div class="card border-0 bg-light">
                                        <div class="card-body">
                                            <h6>Tool Effectiveness</h6>
                                            {% for tool, rate in data.tools_data.tool_effectiveness.items() %}
                                            <div class="mb-2">
                                                <div class="d-flex justify-content-between">
                                                    <span>{{ tool.replace('_', ' ').title() }}</span>
                                                    <span>{{ "%.1f"|format(rate) }}%</span>
                                                </div>
                                                <div class="progress" style="height: 4px;">
                                                    <div class="progress-bar bg-{{ 'success' if rate > 85 else 'warning' if rate > 75 else 'danger' }}" style="width: {{ rate }}%"></div>
                                                </div>
                                            </div>
                                            {% endfor %}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Treatment Plans Tab -->
                        <div class="tab-pane fade {{ 'show active' if data.active_tab == 'plans' else '' }}"
                             id="plans" role="tabpanel">
                            <div class="row">
                                <div class="col-md-8">
                                    <h5 class="mb-3">
                                        <i class="fas fa-clipboard-list text-info me-2"></i>Active Treatment Plans
                                    </h5>

                                    {% for plan in data.plans_data.active_plans_list %}
                                    <div class="card mb-3">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between">
                                                <div>
                                                    <h6 class="card-title">Patient {{ plan.patient_id }}</h6>
                                                    <div class="mb-2">
                                                        <span class="badge bg-{{ 'primary' if plan.plan_type == 'anxiety_treatment' else 'info' if plan.plan_type == 'depression_therapy' else 'warning' if plan.plan_type == 'ptsd_recovery' else 'secondary' }}">
                                                            {{ plan.plan_type.replace('_', ' ').title() }}
                                                        </span>
                                                        <small class="text-muted ms-2">{{ plan.therapist }}</small>
                                                    </div>
                                                    <div class="row">
                                                        <div class="col-md-6">
                                                            <small class="text-muted">Current Phase</small>
                                                            <div class="fw-bold">{{ plan.current_phase }}</div>
                                                        </div>
                                                        <div class="col-md-6">
                                                            <small class="text-muted">Next Session</small>
                                                            <div class="fw-bold text-info">{{ plan.next_session.strftime('%Y-%m-%d') }}</div>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div class="text-end">
                                                    <div class="mb-2">
                                                        <div class="fw-bold text-{{ 'success' if plan.progress_percentage > 66 else 'warning' if plan.progress_percentage > 33 else 'info' }}">
                                                            {{ plan.progress_percentage }}%
                                                        </div>
                                                        <small class="text-muted">Progress</small>
                                                    </div>
                                                    <div class="progress mb-2" style="width: 100px; height: 6px;">
                                                        <div class="progress-bar bg-{{ 'success' if plan.progress_percentage > 66 else 'warning' if plan.progress_percentage > 33 else 'info' }}"
                                                             style="width: {{ plan.progress_percentage }}%"></div>
                                                    </div>
                                                    <small class="text-muted">Score: {{ plan.improvement_score }}/10</small>
                                                </div>
                                            </div>
                                            <div class="mt-3">
                                                <div class="mb-2">
                                                    <small class="text-muted">Tools Used:</small>
                                                    {% for tool in plan.tools_used %}
                                                    <span class="badge bg-light text-dark ms-1">{{ tool }}</span>
                                                    {% endfor %}
                                                </div>
                                                <button class="btn btn-sm btn-outline-primary">View Details</button>
                                                <button class="btn btn-sm btn-outline-secondary">Edit Plan</button>
                                                <button class="btn btn-sm btn-outline-info">Progress Report</button>
                                            </div>
                                        </div>
                                    </div>
                                    {% endfor %}
                                </div>

                                <!-- Treatment Analytics Sidebar -->
                                <div class="col-md-4">
                                    <h6 class="mb-3">Treatment Analytics</h6>

                                    <!-- Plan Types -->
                                    <div class="mb-4">
                                        <h6 class="mb-3">Plan Types</h6>
                                        {% for plan_type, count in data.plans_data.plan_types.items() %}
                                        <div class="mb-2">
                                            <div class="d-flex justify-content-between">
                                                <span>{{ plan_type.replace('_', ' ').title() }}</span>
                                                <span class="badge bg-info">{{ count }}</span>
                                            </div>
                                        </div>
                                        {% endfor %}
                                    </div>

                                    <!-- Outcome Metrics -->
                                    <div class="card border-0 bg-light">
                                        <div class="card-body">
                                            <h6>Outcome Metrics</h6>
                                            {% for metric, value in data.plans_data.outcome_metrics.items() %}
                                            <div class="mb-2">
                                                <div class="d-flex justify-content-between">
                                                    <span>{{ metric.replace('_', ' ').title() }}</span>
                                                    <span>{{ value }}%</span>
                                                </div>
                                                <div class="progress" style="height: 4px;">
                                                    <div class="progress-bar bg-{{ 'success' if value > 80 else 'warning' if value > 65 else 'danger' }}" style="width: {{ value }}%"></div>
                                                </div>
                                            </div>
                                            {% endfor %}
                                        </div>
                                    </div>

                                    <!-- Therapist Workload -->
                                    <div class="mt-4">
                                        <h6 class="mb-3">Therapist Workload</h6>
                                        {% for therapist, workload in data.plans_data.therapist_workload.items() %}
                                        <div class="mb-2">
                                            <div class="d-flex justify-content-between">
                                                <span>{{ therapist }}</span>
                                                <span class="text-{{ 'danger' if workload.utilization > 95 else 'warning' if workload.utilization > 85 else 'success' }}">
                                                    {{ workload.utilization }}%
                                                </span>
                                            </div>
                                            <small class="text-muted">{{ workload.active_patients }} patients</small>
                                        </div>
                                        {% endfor %}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function switchTab(tabName) {
    window.location.href = '?tab=' + tabName;
}
</script>
{% endblock %}'''

# Write the template to the server
with open('/root/MindMend/templates/admin/therapy_community.html', 'w') as f:
    f.write(template_content)

print("Therapy & Community template created with:")
print("✅ Social Groups tab with community management and moderation")
print("✅ Therapy Tools tab with VR environments and biofeedback")
print("✅ Treatment Plans tab with progress tracking and outcomes")
print("✅ Community health monitoring and crisis response metrics")
print("✅ Comprehensive therapist workload and patient analytics")
print("✅ Responsive design consistent with other admin interfaces")