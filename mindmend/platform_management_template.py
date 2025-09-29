#!/usr/bin/env python3

# Create Platform Management Template with tabbed interface

template_content = '''{% extends "admin/base.html" %}

{% block title %}Platform Management - Mind Mend Admin{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Header Section -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="h3 mb-0">
                        <i class="fas fa-users-cog me-2 text-primary"></i>
                        Platform Management
                    </h1>
                    <p class="text-muted mb-0">Users, Research & Analytics Dashboard</p>
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-outline-primary btn-sm">
                        <i class="fas fa-download me-1"></i>Export Data
                    </button>
                    <button class="btn btn-primary btn-sm">
                        <i class="fas fa-sync-alt me-1"></i>Refresh
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Overview Cards -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card bg-primary text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h4 class="mb-0">{{ "{:,}".format(data.overview_stats.total_users) }}</h4>
                            <p class="mb-0">Total Users</p>
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
                            <h4 class="mb-0">{{ data.overview_stats.research_insights }}</h4>
                            <p class="mb-0">Research Insights</p>
                        </div>
                        <div class="align-self-center">
                            <i class="fas fa-lightbulb fa-2x"></i>
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
                            <h4 class="mb-0">{{ "%.1f"|format(data.overview_stats.platform_score) }}%</h4>
                            <p class="mb-0">Platform Score</p>
                        </div>
                        <div class="align-self-center">
                            <i class="fas fa-chart-line fa-2x"></i>
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
                            <h4 class="mb-0">+{{ "%.1f"|format(data.overview_stats.monthly_growth) }}%</h4>
                            <p class="mb-0">Monthly Growth</p>
                        </div>
                        <div class="align-self-center">
                            <i class="fas fa-trending-up fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Platform Alerts -->
    {% if data.platform_alerts %}
    <div class="row mb-4">
        <div class="col-12">
            {% for alert in data.platform_alerts %}
            <div class="alert alert-{{ 'warning' if alert.level == 'warning' else 'info' }} alert-dismissible fade show">
                <i class="fas fa-{{ 'exclamation-triangle' if alert.level == 'warning' else 'info-circle' }} me-2"></i>
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
                    <ul class="nav nav-tabs card-header-tabs" id="platformTabs">
                        <li class="nav-item">
                            <a class="nav-link {{ 'active' if data.active_tab == 'users' else '' }}"
                               href="?tab=users" id="users-tab">
                                <i class="fas fa-users me-2"></i>User Management
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link {{ 'active' if data.active_tab == 'research' else '' }}"
                               href="?tab=research" id="research-tab">
                                <i class="fas fa-flask me-2"></i>Research Management
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link {{ 'active' if data.active_tab == 'analytics' else '' }}"
                               href="?tab=analytics" id="analytics-tab">
                                <i class="fas fa-chart-bar me-2"></i>Analytics Dashboard
                            </a>
                        </li>
                    </ul>
                </div>
                <div class="card-body">
                    <div class="tab-content" id="platformTabContent">

                        <!-- Users Tab -->
                        <div class="tab-pane fade {{ 'show active' if data.active_tab == 'users' else '' }}"
                             id="users" role="tabpanel">
                            <div class="row">
                                <!-- User Statistics -->
                                <div class="col-md-8">
                                    <h5 class="mb-3">
                                        <i class="fas fa-users text-primary me-2"></i>User Overview
                                    </h5>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="card border-0 bg-light">
                                                <div class="card-body">
                                                    <h6>Active Users</h6>
                                                    <h4 class="text-success">{{ "{:,}".format(data.user_data.active_users) }}</h4>
                                                    <small class="text-muted">{{ "%.1f"|format((data.user_data.active_users/data.user_data.total_users)*100) }}% of total</small>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="card border-0 bg-light">
                                                <div class="card-body">
                                                    <h6>Premium Users</h6>
                                                    <h4 class="text-warning">{{ "{:,}".format(data.user_data.premium_users) }}</h4>
                                                    <small class="text-muted">{{ "%.1f"|format((data.user_data.premium_users/data.user_data.total_users)*100) }}% conversion rate</small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Recent Registrations -->
                                    <h6 class="mt-4 mb-3">Recent Registrations</h6>
                                    <div class="table-responsive">
                                        <table class="table table-hover">
                                            <thead>
                                                <tr>
                                                    <th>Name</th>
                                                    <th>Email</th>
                                                    <th>Plan</th>
                                                    <th>Status</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {% for user in data.user_data.recent_registrations %}
                                                <tr>
                                                    <td>
                                                        {{ user.name }}
                                                        {% if user.get('role') == 'counselor' %}
                                                        <span class="badge bg-info ms-1">Counselor</span>
                                                        {% endif %}
                                                    </td>
                                                    <td>{{ user.email }}</td>
                                                    <td>
                                                        <span class="badge bg-{{ 'warning' if user.plan == 'Premium' else 'secondary' }}">
                                                            {{ user.plan }}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <span class="badge bg-{{ 'success' if user.status == 'active' else 'warning' }}">
                                                            {{ user.status.replace('_', ' ').title() }}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <button class="btn btn-sm btn-outline-primary">View</button>
                                                        <button class="btn btn-sm btn-outline-secondary">Edit</button>
                                                    </td>
                                                </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>

                                <!-- User Analytics Sidebar -->
                                <div class="col-md-4">
                                    <h6 class="mb-3">Demographics</h6>
                                    {% for age_group, percentage in data.user_data.user_analytics.demographic_breakdown.items() %}
                                    <div class="mb-2">
                                        <div class="d-flex justify-content-between">
                                            <span>{{ age_group.replace('_', '-').replace('age-', 'Age ') }}</span>
                                            <span>{{ percentage }}%</span>
                                        </div>
                                        <div class="progress" style="height: 5px;">
                                            <div class="progress-bar" style="width: {{ percentage }}%"></div>
                                        </div>
                                    </div>
                                    {% endfor %}

                                    <h6 class="mt-4 mb-3">Geographic Distribution</h6>
                                    {% for region, percentage in data.user_data.user_analytics.geographic_distribution.items() %}
                                    <div class="mb-2">
                                        <div class="d-flex justify-content-between">
                                            <span>{{ region.title() }}</span>
                                            <span>{{ percentage }}%</span>
                                        </div>
                                        <div class="progress" style="height: 5px;">
                                            <div class="progress-bar bg-info" style="width: {{ percentage }}%"></div>
                                        </div>
                                    </div>
                                    {% endfor %}
                                </div>
                            </div>
                        </div>

                        <!-- Research Tab -->
                        <div class="tab-pane fade {{ 'show active' if data.active_tab == 'research' else '' }}"
                             id="research" role="tabpanel">
                            <div class="row">
                                <div class="col-md-8">
                                    <h5 class="mb-3">
                                        <i class="fas fa-flask text-success me-2"></i>Research Overview
                                    </h5>

                                    <!-- Research Papers -->
                                    <h6 class="mb-3">Recent Research Papers</h6>
                                    {% for paper in data.research_data.recent_papers %}
                                    <div class="card mb-3">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between">
                                                <div>
                                                    <h6 class="card-title">{{ paper.title }}</h6>
                                                    <p class="text-muted mb-1">{{ paper.authors }}</p>
                                                    <small class="text-muted">{{ paper.journal }} • {{ paper.date.strftime('%B %d, %Y') }}</small>
                                                </div>
                                                <div class="text-end">
                                                    <div class="mb-2">
                                                        <span class="badge bg-{{ 'success' if paper.relevance_score > 90 else 'warning' if paper.relevance_score > 80 else 'secondary' }}">
                                                            {{ paper.relevance_score }}% Relevance
                                                        </span>
                                                    </div>
                                                    <span class="badge bg-{{ 'success' if paper.status == 'integrated' else 'warning' }}">
                                                        {{ paper.status.replace('_', ' ').title() }}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    {% endfor %}

                                    <!-- Dataset Sources -->
                                    <h6 class="mt-4 mb-3">Active Datasets</h6>
                                    <div class="table-responsive">
                                        <table class="table table-hover">
                                            <thead>
                                                <tr>
                                                    <th>Dataset Name</th>
                                                    <th>Records</th>
                                                    <th>Quality Score</th>
                                                    <th>Usage</th>
                                                    <th>Last Updated</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {% for dataset in data.research_data.dataset_sources %}
                                                <tr>
                                                    <td>{{ dataset.name }}</td>
                                                    <td>{{ "{:,}".format(dataset.records) }}</td>
                                                    <td>
                                                        <span class="badge bg-{{ 'success' if dataset.quality_score > 95 else 'warning' if dataset.quality_score > 85 else 'secondary' }}">
                                                            {{ dataset.quality_score }}%
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <span class="badge bg-{{ 'primary' if dataset.usage_frequency == 'high' else 'info' if dataset.usage_frequency == 'medium' else 'secondary' }}">
                                                            {{ dataset.usage_frequency.title() }}
                                                        </span>
                                                    </td>
                                                    <td>{{ dataset.last_updated.strftime('%Y-%m-%d') }}</td>
                                                </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>

                                <!-- Research Categories Sidebar -->
                                <div class="col-md-4">
                                    <h6 class="mb-3">Research Categories</h6>
                                    {% for category, count in data.research_data.research_categories.items() %}
                                    <div class="mb-3">
                                        <div class="d-flex justify-content-between">
                                            <span>{{ category.replace('_', ' ').title() }}</span>
                                            <span class="badge bg-primary">{{ count }}</span>
                                        </div>
                                    </div>
                                    {% endfor %}

                                    <div class="card border-0 bg-light mt-4">
                                        <div class="card-body">
                                            <h6>Quick Stats</h6>
                                            <div class="mb-2">
                                                <small class="text-muted">Total Papers</small>
                                                <div class="fw-bold">{{ data.research_data.total_papers }}</div>
                                            </div>
                                            <div class="mb-2">
                                                <small class="text-muted">Active Analyses</small>
                                                <div class="fw-bold text-warning">{{ data.research_data.active_analyses }}</div>
                                            </div>
                                            <div class="mb-2">
                                                <small class="text-muted">Validated Insights</small>
                                                <div class="fw-bold text-success">{{ data.research_data.validated_insights }}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Analytics Tab -->
                        <div class="tab-pane fade {{ 'show active' if data.active_tab == 'analytics' else '' }}"
                             id="analytics" role="tabpanel">
                            <h5 class="mb-4">
                                <i class="fas fa-chart-bar text-info me-2"></i>Analytics Dashboard
                            </h5>

                            <div class="row">
                                <!-- Platform Metrics -->
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Platform Performance</h6>
                                        </div>
                                        <div class="card-body">
                                            {% for metric, value in data.analytics_data.platform_metrics.items() %}
                                            <div class="d-flex justify-content-between mb-2">
                                                <span>{{ metric.replace('_', ' ').title() }}</span>
                                                <span class="fw-bold">
                                                    {% if 'rate' in metric or 'score' in metric %}
                                                        {{ "%.1f"|format(value) }}%
                                                    {% else %}
                                                        {{ "{:,}".format(value) }}
                                                    {% endif %}
                                                </span>
                                            </div>
                                            {% endfor %}
                                        </div>
                                    </div>
                                </div>

                                <!-- Usage Patterns -->
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Feature Usage</h6>
                                        </div>
                                        <div class="card-body">
                                            {% for feature in data.analytics_data.usage_patterns.most_used_features %}
                                            <div class="mb-3">
                                                <div class="d-flex justify-content-between">
                                                    <span>{{ feature.feature }}</span>
                                                    <span>{{ feature.usage }}%</span>
                                                </div>
                                                <div class="progress" style="height: 6px;">
                                                    <div class="progress-bar" style="width: {{ feature.usage }}%"></div>
                                                </div>
                                            </div>
                                            {% endfor %}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Health Metrics Row -->
                            <div class="row mt-4">
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Health Improvement Indicators</h6>
                                        </div>
                                        <div class="card-body">
                                            {% for indicator, percentage in data.analytics_data.health_metrics.improvement_indicators.items() %}
                                            <div class="mb-3">
                                                <div class="d-flex justify-content-between">
                                                    <span>{{ indicator.replace('_', ' ').title() }}</span>
                                                    <span class="text-success fw-bold">{{ percentage }}%</span>
                                                </div>
                                                <div class="progress" style="height: 6px;">
                                                    <div class="progress-bar bg-success" style="width: {{ percentage }}%"></div>
                                                </div>
                                            </div>
                                            {% endfor %}
                                        </div>
                                    </div>
                                </div>

                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Financial Analytics</h6>
                                        </div>
                                        <div class="card-body">
                                            {% for metric, value in data.analytics_data.financial_analytics.revenue_trends.items() %}
                                            <div class="d-flex justify-content-between mb-2">
                                                <span>{{ metric.replace('_', ' ').title() }}</span>
                                                <span class="fw-bold">
                                                    {% if 'rate' in metric %}
                                                        {{ "%.1f"|format(value) }}%
                                                    {% elif 'revenue' in metric or 'value' in metric %}
                                                        ${{ "{:,.0f}".format(value) }}
                                                    {% else %}
                                                        {{ "%.1f"|format(value) }}%
                                                    {% endif %}
                                                </span>
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
</div>

<script>
function switchTab(tabName) {
    window.location.href = '?tab=' + tabName;
}
</script>
{% endblock %}'''

# Write the template to the server
with open('/root/MindMend/templates/admin/platform_management.html', 'w') as f:
    f.write(template_content)

print("Platform Management template created with:")
print("✅ Responsive tabbed interface for Users, Research & Analytics")
print("✅ Overview cards with key platform metrics")
print("✅ Detailed data presentation with charts and tables")
print("✅ Integrated alerts and notifications system")
print("✅ Modern Bootstrap 5 styling with FontAwesome icons")
print("✅ Tab switching functionality and URL-based navigation")