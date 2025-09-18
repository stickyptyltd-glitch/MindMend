#!/usr/bin/env python3

# Create AI & Technology Template with tabbed interface

template_content = '''{% extends "admin/base.html" %}

{% block title %}AI & Technology - Mind Mend Admin{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Header Section -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="h3 mb-0">
                        <i class="fas fa-brain me-2 text-success"></i>
                        AI & Technology Management
                    </h1>
                    <p class="text-muted mb-0">Models, Features & Integrations Dashboard</p>
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-outline-success btn-sm">
                        <i class="fas fa-download me-1"></i>Export Logs
                    </button>
                    <button class="btn btn-success btn-sm">
                        <i class="fas fa-sync-alt me-1"></i>Refresh
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Overview Cards -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card bg-success text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h4 class="mb-0">{{ data.overview_stats.total_models }}</h4>
                            <p class="mb-0">AI Models</p>
                        </div>
                        <div class="align-self-center">
                            <i class="fas fa-robot fa-2x"></i>
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
                            <h4 class="mb-0">{{ data.overview_stats.active_features }}</h4>
                            <p class="mb-0">Active Features</p>
                        </div>
                        <div class="align-self-center">
                            <i class="fas fa-cogs fa-2x"></i>
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
                            <h4 class="mb-0">{{ data.overview_stats.integrations }}</h4>
                            <p class="mb-0">Integrations</p>
                        </div>
                        <div class="align-self-center">
                            <i class="fas fa-plug fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-primary text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h4 class="mb-0">{{ "%.1f"|format(data.overview_stats.tech_score) }}%</h4>
                            <p class="mb-0">Tech Score</p>
                        </div>
                        <div class="align-self-center">
                            <i class="fas fa-chart-line fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Technology Alerts -->
    {% if data.tech_alerts %}
    <div class="row mb-4">
        <div class="col-12">
            {% for alert in data.tech_alerts %}
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
                    <ul class="nav nav-tabs card-header-tabs" id="techTabs">
                        <li class="nav-item">
                            <a class="nav-link {{ 'active' if data.active_tab == 'models' else '' }}"
                               href="?tab=models" id="models-tab">
                                <i class="fas fa-robot me-2"></i>AI Models
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link {{ 'active' if data.active_tab == 'features' else '' }}"
                               href="?tab=features" id="features-tab">
                                <i class="fas fa-cogs me-2"></i>Features
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link {{ 'active' if data.active_tab == 'integrations' else '' }}"
                               href="?tab=integrations" id="integrations-tab">
                                <i class="fas fa-plug me-2"></i>Integrations
                            </a>
                        </li>
                    </ul>
                </div>
                <div class="card-body">
                    <div class="tab-content" id="techTabContent">

                        <!-- AI Models Tab -->
                        <div class="tab-pane fade {{ 'show active' if data.active_tab == 'models' else '' }}"
                             id="models" role="tabpanel">
                            <div class="row">
                                <!-- Model Statistics -->
                                <div class="col-md-8">
                                    <h5 class="mb-3">
                                        <i class="fas fa-robot text-success me-2"></i>AI Model Overview
                                    </h5>

                                    <!-- Performance Metrics -->
                                    <div class="row mb-4">
                                        <div class="col-md-6">
                                            <div class="card border-0 bg-light">
                                                <div class="card-body">
                                                    <h6>Model Performance</h6>
                                                    <div class="mb-2">
                                                        <small class="text-muted">Average Accuracy</small>
                                                        <div class="fw-bold text-success">{{ "%.1f"|format(data.ai_models_data.model_accuracy_avg) }}%</div>
                                                    </div>
                                                    <div class="mb-2">
                                                        <small class="text-muted">Response Time</small>
                                                        <div class="fw-bold">{{ data.ai_models_data.performance_metrics.response_time_avg }}</div>
                                                    </div>
                                                    <div class="mb-2">
                                                        <small class="text-muted">Daily Predictions</small>
                                                        <div class="fw-bold text-info">{{ "{:,}".format(data.ai_models_data.daily_predictions) }}</div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="card border-0 bg-light">
                                                <div class="card-body">
                                                    <h6>Resource Usage</h6>
                                                    <div class="mb-2">
                                                        <small class="text-muted">Memory Usage</small>
                                                        <div class="fw-bold">{{ data.ai_models_data.performance_metrics.memory_usage }}</div>
                                                    </div>
                                                    <div class="mb-2">
                                                        <small class="text-muted">CPU Utilization</small>
                                                        <div class="progress mb-1" style="height: 6px;">
                                                            <div class="progress-bar" style="width: {{ data.ai_models_data.performance_metrics.cpu_utilization }}%"></div>
                                                        </div>
                                                        <small>{{ data.ai_models_data.performance_metrics.cpu_utilization }}%</small>
                                                    </div>
                                                    <div class="mb-2">
                                                        <small class="text-muted">GPU Utilization</small>
                                                        <div class="progress mb-1" style="height: 6px;">
                                                            <div class="progress-bar bg-warning" style="width: {{ data.ai_models_data.performance_metrics.gpu_utilization }}%"></div>
                                                        </div>
                                                        <small>{{ data.ai_models_data.performance_metrics.gpu_utilization }}%</small>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Recent Models -->
                                    <h6 class="mb-3">Active Models</h6>
                                    <div class="table-responsive">
                                        <table class="table table-hover">
                                            <thead>
                                                <tr>
                                                    <th>Model Name</th>
                                                    <th>Type</th>
                                                    <th>Specialization</th>
                                                    <th>Accuracy</th>
                                                    <th>Status</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {% for model in data.ai_models_data.recent_models %}
                                                <tr>
                                                    <td>
                                                        <strong>{{ model.name }}</strong>
                                                        {% if model.type == 'huggingface' %}
                                                        <span class="badge bg-warning ms-1">HF</span>
                                                        {% endif %}
                                                    </td>
                                                    <td>
                                                        <span class="badge bg-{{ 'primary' if model.type == 'ollama' else 'info' if model.type == 'custom_ml' else 'warning' }}">
                                                            {{ model.type.replace('_', ' ').title() }}
                                                        </span>
                                                    </td>
                                                    <td>{{ model.specialization.replace('_', ' ').title() }}</td>
                                                    <td>
                                                        <span class="text-{{ 'success' if model.accuracy > 90 else 'warning' if model.accuracy > 80 else 'danger' }}">
                                                            {{ "%.1f"|format(model.accuracy) }}%
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <span class="badge bg-{{ 'success' if model.status == 'active' else 'warning' if model.status == 'installing' else 'secondary' }}">
                                                            {{ model.status.title() }}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <button class="btn btn-sm btn-outline-primary">Test</button>
                                                        <button class="btn btn-sm btn-outline-secondary">Configure</button>
                                                    </td>
                                                </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                    </div>

                                    <!-- Hugging Face Integration -->
                                    <div class="card mt-4">
                                        <div class="card-header">
                                            <h6 class="mb-0">
                                                <i class="fas fa-rocket me-2"></i>Hugging Face Integration
                                            </h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="row">
                                                <div class="col-md-4">
                                                    <small class="text-muted">Status</small>
                                                    <div class="fw-bold text-success">{{ data.ai_models_data.huggingface_integration.status.title() }}</div>
                                                </div>
                                                <div class="col-md-4">
                                                    <small class="text-muted">Daily Requests</small>
                                                    <div class="fw-bold">{{ data.ai_models_data.huggingface_integration.daily_requests }}</div>
                                                </div>
                                                <div class="col-md-4">
                                                    <small class="text-muted">API Quota Remaining</small>
                                                    <div class="fw-bold text-info">{{ "{:,}".format(data.ai_models_data.huggingface_integration.api_quota_remaining) }}</div>
                                                </div>
                                            </div>
                                            <div class="mt-3">
                                                <button class="btn btn-outline-warning btn-sm me-2">
                                                    <i class="fas fa-search me-1"></i>Browse Models
                                                </button>
                                                <button class="btn btn-outline-success btn-sm">
                                                    <i class="fas fa-download me-1"></i>Install Model
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Model Categories Sidebar -->
                                <div class="col-md-4">
                                    <h6 class="mb-3">Model Categories</h6>
                                    {% for category, count in data.ai_models_data.models_by_category.items() %}
                                    <div class="mb-3">
                                        <div class="d-flex justify-content-between">
                                            <span>{{ category.title() }}</span>
                                            <span class="badge bg-success">{{ count }}</span>
                                        </div>
                                    </div>
                                    {% endfor %}

                                    <div class="card border-0 bg-light mt-4">
                                        <div class="card-body">
                                            <h6>Quick Stats</h6>
                                            <div class="mb-2">
                                                <small class="text-muted">Active Models</small>
                                                <div class="fw-bold text-success">{{ data.ai_models_data.active_models }}</div>
                                            </div>
                                            <div class="mb-2">
                                                <small class="text-muted">Training Jobs</small>
                                                <div class="fw-bold text-warning">{{ data.ai_models_data.training_jobs }}</div>
                                            </div>
                                            <div class="mb-2">
                                                <small class="text-muted">Hugging Face Models</small>
                                                <div class="fw-bold text-info">{{ data.ai_models_data.huggingface_models }}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Features Tab -->
                        <div class="tab-pane fade {{ 'show active' if data.active_tab == 'features' else '' }}"
                             id="features" role="tabpanel">
                            <div class="row">
                                <div class="col-md-8">
                                    <h5 class="mb-3">
                                        <i class="fas fa-cogs text-info me-2"></i>Feature Modules
                                    </h5>

                                    <!-- Feature Modules -->
                                    {% for module in data.features_data.feature_modules %}
                                    <div class="card mb-3">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between">
                                                <div>
                                                    <h6 class="card-title">{{ module.name }}</h6>
                                                    <p class="text-muted mb-1">{{ module.description }}</p>
                                                    <div class="mb-2">
                                                        <span class="badge bg-{{ 'primary' if module.category == 'ai_enhancements' else 'info' if module.category == 'health_tracking' else 'secondary' }}">
                                                            {{ module.category.replace('_', ' ').title() }}
                                                        </span>
                                                        <small class="text-muted ms-2">v{{ module.version }}</small>
                                                    </div>
                                                    <small class="text-muted">Updated: {{ module.last_updated.strftime('%Y-%m-%d') }}</small>
                                                </div>
                                                <div class="text-end">
                                                    <div class="mb-2">
                                                        <span class="badge bg-{{ 'success' if module.status == 'active' else 'warning' if module.status == 'beta' else 'secondary' }}">
                                                            {{ module.status.title() }}
                                                        </span>
                                                    </div>
                                                    {% if module.get('usage_rate') %}
                                                    <div class="text-success fw-bold">{{ module.usage_rate }}% Usage</div>
                                                    {% elif module.get('connections') %}
                                                    <div class="text-info fw-bold">{{ module.connections }} Connections</div>
                                                    {% elif module.get('performance_boost') %}
                                                    <div class="text-warning fw-bold">+{{ module.performance_boost }}% Performance</div>
                                                    {% endif %}
                                                </div>
                                            </div>
                                            <div class="mt-3">
                                                <button class="btn btn-sm btn-outline-primary">Configure</button>
                                                <button class="btn btn-sm btn-outline-secondary">View Logs</button>
                                                {% if module.status != 'active' %}
                                                <button class="btn btn-sm btn-outline-success">Activate</button>
                                                {% endif %}
                                            </div>
                                        </div>
                                    </div>
                                    {% endfor %}

                                    <!-- Integration Status -->
                                    <h6 class="mt-4 mb-3">Integration Status</h6>
                                    <div class="row">
                                        {% for integration, status in data.features_data.integration_status.items() %}
                                        <div class="col-md-6 mb-2">
                                            <div class="d-flex justify-content-between align-items-center">
                                                <span>{{ integration.replace('_', ' ').title() }}</span>
                                                <span class="badge bg-{{ 'success' if status == 'active' else 'warning' }}">
                                                    {{ status.title() }}
                                                </span>
                                            </div>
                                        </div>
                                        {% endfor %}
                                    </div>
                                </div>

                                <!-- Features Sidebar -->
                                <div class="col-md-4">
                                    <h6 class="mb-3">Module Categories</h6>
                                    {% for category, count in data.features_data.module_categories.items() %}
                                    <div class="mb-3">
                                        <div class="d-flex justify-content-between">
                                            <span>{{ category.replace('_', ' ').title() }}</span>
                                            <span class="badge bg-info">{{ count }}</span>
                                        </div>
                                    </div>
                                    {% endfor %}

                                    <div class="card border-0 bg-light mt-4">
                                        <div class="card-body">
                                            <h6>Performance Impact</h6>
                                            {% for metric, value in data.features_data.performance_impact.items() %}
                                            <div class="mb-2">
                                                <div class="d-flex justify-content-between">
                                                    <span>{{ metric.replace('_', ' ').title() }}</span>
                                                    <span>{{ value }}%</span>
                                                </div>
                                                <div class="progress" style="height: 4px;">
                                                    <div class="progress-bar bg-{{ 'warning' if value > 15 else 'info' }}" style="width: {{ value }}%"></div>
                                                </div>
                                            </div>
                                            {% endfor %}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Integrations Tab -->
                        <div class="tab-pane fade {{ 'show active' if data.active_tab == 'integrations' else '' }}"
                             id="integrations" role="tabpanel">
                            <h5 class="mb-4">
                                <i class="fas fa-plug text-warning me-2"></i>External Integrations
                            </h5>

                            <!-- API Monitoring Overview -->
                            <div class="row mb-4">
                                <div class="col-md-3">
                                    <div class="card border-0 bg-light">
                                        <div class="card-body text-center">
                                            <h4 class="text-primary">{{ "{:,}".format(data.integrations_data.api_monitoring.total_requests_today) }}</h4>
                                            <small class="text-muted">Total Requests Today</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card border-0 bg-light">
                                        <div class="card-body text-center">
                                            <h4 class="text-success">{{ "%.1f"|format(data.integrations_data.api_monitoring.success_rate) }}%</h4>
                                            <small class="text-muted">Success Rate</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card border-0 bg-light">
                                        <div class="card-body text-center">
                                            <h4 class="text-info">{{ data.integrations_data.api_monitoring.avg_response_time }}</h4>
                                            <small class="text-muted">Avg Response Time</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card border-0 bg-light">
                                        <div class="card-body text-center">
                                            <h4 class="text-{{ 'danger' if data.integrations_data.api_monitoring.failed_requests > 20 else 'warning' if data.integrations_data.api_monitoring.failed_requests > 5 else 'success' }}">
                                                {{ data.integrations_data.api_monitoring.failed_requests }}
                                            </h4>
                                            <small class="text-muted">Failed Requests</small>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- External Services -->
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Service Name</th>
                                            <th>Category</th>
                                            <th>Status</th>
                                            <th>Response Time</th>
                                            <th>Usage Today</th>
                                            <th>Last Sync</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for service in data.integrations_data.external_services %}
                                        <tr>
                                            <td>
                                                <strong>{{ service.name }}</strong>
                                                <br><small class="text-muted">{{ service.api_version }}</small>
                                            </td>
                                            <td>
                                                <span class="badge bg-{{ 'primary' if service.category == 'ai_services' else 'info' if service.category == 'health_platforms' else 'secondary' }}">
                                                    {{ service.category.replace('_', ' ').title() }}
                                                </span>
                                            </td>
                                            <td>
                                                <span class="badge bg-{{ 'success' if service.status == 'active' else 'warning' if service.status == 'maintenance' else 'danger' }}">
                                                    {{ service.status.title() }}
                                                </span>
                                            </td>
                                            <td>{{ service.response_time }}</td>
                                            <td>
                                                {% if service.get('requests_today') %}
                                                    {{ service.requests_today }} requests
                                                {% elif service.get('connected_devices') %}
                                                    {{ service.connected_devices }} devices
                                                {% elif service.get('bandwidth_used') %}
                                                    {{ service.bandwidth_used }}
                                                {% elif service.get('total_sessions_today') %}
                                                    {{ service.total_sessions_today }} sessions
                                                {% endif %}
                                            </td>
                                            <td>{{ service.last_sync.strftime('%H:%M') }}</td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary">Test</button>
                                                <button class="btn btn-sm btn-outline-secondary">Configure</button>
                                            </td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
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
with open('/root/MindMend/templates/admin/ai_technology.html', 'w') as f:
    f.write(template_content)

print("AI & Technology template created with:")
print("✅ Comprehensive AI models tab with Hugging Face integration")
print("✅ Feature modules tab with performance monitoring")
print("✅ External integrations tab with API monitoring")
print("✅ Responsive design with real-time metrics")
print("✅ Consistent styling with existing admin interfaces")
print("✅ Tab switching functionality and status indicators")