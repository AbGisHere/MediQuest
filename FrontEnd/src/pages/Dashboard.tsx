import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  Heart, 
  Activity, 
  Users, 
  AlertTriangle, 
  TrendingUp, 
  Calendar,
  FileText,
  Clock,
  ChevronRight,
  Bell,
  Search,
  Filter,
  Download,
  Eye,
  BarChart3,
  PieChart,
  TrendingDown,
  CheckCircle,
  XCircle,
  AlertCircle,
  User,
  Stethoscope,
  Pill,
  Thermometer,
  Droplet,
  Zap,
  Shield,
  Target,
  Award,
  Star
} from 'lucide-react';
import apiService from '../services/api';

interface DashboardStats {
  totalPatients: number;
  activePatients: number;
  totalVitals: number;
  criticalAlerts: number;
  pendingReports: number;
  upcomingAppointments: number;
  systemHealth: number;
  userSatisfaction: number;
}

interface RecentActivity {
  id: string;
  type: 'vital' | 'alert' | 'report' | 'appointment' | 'patient';
  title: string;
  description: string;
  timestamp: string;
  patient?: string;
  status: 'normal' | 'warning' | 'critical' | 'success';
}

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ElementType;
  color: string;
  href: string;
  count?: number;
}

interface HealthMetric {
  label: string;
  value: number;
  unit: string;
  status: 'normal' | 'warning' | 'critical';
  trend: 'up' | 'down' | 'stable';
  change: number;
}

const Dashboard: React.FC = () => {
  const { user, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({
    totalPatients: 0,
    activePatients: 0,
    totalVitals: 0,
    criticalAlerts: 0,
    pendingReports: 0,
    upcomingAppointments: 0,
    systemHealth: 95,
    userSatisfaction: 92
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [healthMetrics, setHealthMetrics] = useState<HealthMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);

        if (user?.role !== 'patient') {
          // Fetch data for doctors/admins
          const patients = await apiService.getPatientsWithConsent(0, 50);
          
          // Get vitals for multiple patients
          const vitalsPromises = patients.slice(0, 5).map(patient => 
            apiService.getPatientVitals(patient.id, undefined, 10)
          );
          const allVitals = await Promise.all(vitalsPromises);
          const flatVitals = allVitals.flat();
          
          const alerts = await apiService.getActiveEmergencyOverrides();

          // Generate sample recent activity
          const sampleActivity: RecentActivity[] = [
            {
              id: '1',
              type: 'vital',
              title: 'Critical Blood Pressure',
              description: 'John Doe - BP 180/120 detected',
              timestamp: '2 minutes ago',
              patient: 'John Doe',
              status: 'critical'
            },
            {
              id: '2',
              type: 'alert',
              title: 'Medication Reminder',
              description: 'Sarah Johnson - Diabetes medication due',
              timestamp: '15 minutes ago',
              patient: 'Sarah Johnson',
              status: 'warning'
            },
            {
              id: '3',
              type: 'report',
              title: 'Blood Report Available',
              description: 'Michael Williams - CBC results ready',
              timestamp: '1 hour ago',
              patient: 'Michael Williams',
              status: 'success'
            },
            {
              id: '4',
              type: 'appointment',
              title: 'Appointment Scheduled',
              description: 'Emily Davis - Cardiology consultation',
              timestamp: '2 hours ago',
              patient: 'Emily Davis',
              status: 'normal'
            },
            {
              id: '5',
              type: 'patient',
              title: 'New Patient Registered',
              description: 'Robert Brown - Initial assessment needed',
              timestamp: '3 hours ago',
              patient: 'Robert Brown',
              status: 'normal'
            }
          ];

          // Generate sample health metrics
          const sampleMetrics: HealthMetric[] = [
            {
              label: 'Average Heart Rate',
              value: 72,
              unit: 'bpm',
              status: 'normal',
              trend: 'stable',
              change: 0
            },
            {
              label: 'Blood Pressure',
              value: 125,
              unit: 'mmHg',
              status: 'warning',
              trend: 'up',
              change: 5
            },
            {
              label: 'Glucose Level',
              value: 95,
              unit: 'mg/dL',
              status: 'normal',
              trend: 'down',
              change: -3
            },
            {
              label: 'Oxygen Saturation',
              value: 98,
              unit: '%',
              status: 'normal',
              trend: 'stable',
              change: 0
            }
          ];

          setStats({
            totalPatients: patients.length,
            activePatients: Math.floor(patients.length * 0.8),
            totalVitals: flatVitals.length,
            criticalAlerts: alerts.length + 2, // Add sample alerts
            pendingReports: Math.floor(patients.length * 0.3),
            upcomingAppointments: Math.floor(patients.length * 0.4),
            systemHealth: 95,
            userSatisfaction: 92
          });

          setRecentActivity(sampleActivity);
          setHealthMetrics(sampleMetrics);
        } else {
          // For patients, show their own data
          setRecentActivity([
            {
              id: '1',
              type: 'vital',
              title: 'Vitals Updated',
              description: 'Your latest vitals have been recorded',
              timestamp: '1 hour ago',
              status: 'success'
            },
            {
              id: '2',
              type: 'report',
              title: 'Lab Results Available',
              description: 'Your blood test results are ready',
              timestamp: '3 hours ago',
              status: 'normal'
            }
          ]);
        }
      } catch (error: any) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (!authLoading && user) {
      fetchDashboardData();
    }
  }, [user, authLoading]);

  const quickActions: QuickAction[] = [
    {
      id: '1',
      title: 'Add Vitals',
      description: 'Record new vital signs',
      icon: Heart,
      color: 'bg-red-500',
      href: '/vitals'
    },
    {
      id: '2',
      title: 'View Patients',
      description: 'Manage patient records',
      icon: Users,
      color: 'bg-blue-500',
      href: '/patients',
      count: stats.totalPatients
    },
    {
      id: '3',
      title: 'Blood Reports',
      description: 'Review lab results',
      icon: FileText,
      color: 'bg-purple-500',
      href: '/blood-reports'
    },
    {
      id: '4',
      title: 'Generate Reports',
      description: 'Create analytics reports',
      icon: BarChart3,
      color: 'bg-green-500',
      href: '/reports'
    }
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'vital': return Heart;
      case 'alert': return AlertTriangle;
      case 'report': return FileText;
      case 'appointment': return Calendar;
      case 'patient': return Users;
      default: return Activity;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'normal': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'critical': return 'text-red-600 bg-red-100';
      case 'success': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return TrendingUp;
      case 'down': return TrendingDown;
      default: return Activity;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return 'text-red-600';
      case 'down': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.username || 'User'}!
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Here's what's happening with your patients today
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search patients, reports..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-64"
            />
          </div>
          <button className="relative p-2 text-gray-600 hover:text-gray-900">
            <Bell className="h-5 w-5" />
            {stats.criticalAlerts > 0 && (
              <span className="absolute top-0 right-0 h-2 w-2 bg-red-500 rounded-full"></span>
            )}
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Patients</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalPatients}</p>
              <p className="text-xs text-green-600 mt-1">
                <TrendingUp className="h-3 w-3 inline mr-1" />
                +12% from last month
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Patients</p>
              <p className="text-2xl font-bold text-gray-900">{stats.activePatients}</p>
              <p className="text-xs text-gray-600 mt-1">
                <Activity className="h-3 w-3 inline mr-1" />
                Currently monitored
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <Heart className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Critical Alerts</p>
              <p className="text-2xl font-bold text-gray-900">{stats.criticalAlerts}</p>
              <p className="text-xs text-red-600 mt-1">
                <AlertTriangle className="h-3 w-3 inline mr-1" />
                Requires attention
              </p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Reports</p>
              <p className="text-2xl font-bold text-gray-900">{stats.pendingReports}</p>
              <p className="text-xs text-yellow-600 mt-1">
                <Clock className="h-3 w-3 inline mr-1" />
                Awaiting review
              </p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <FileText className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <button
                key={action.id}
                onClick={() => navigate(action.href)}
                className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow w-full text-left"
              >
                <div className={`p-2 ${action.color} rounded-lg`}>
                  <Icon className="h-5 w-5 text-white" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{action.title}</p>
                  <p className="text-xs text-gray-600">{action.description}</p>
                </div>
                {action.count !== undefined && (
                  <span className="text-sm font-semibold text-gray-900">{action.count}</span>
                )}
                <ChevronRight className="h-4 w-4 text-gray-400" />
              </button>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2 card">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
              <button className="text-sm text-primary-600 hover:text-primary-700">
                View all
              </button>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {recentActivity.map((activity) => {
              const Icon = getActivityIcon(activity.type);
              return (
                <div key={activity.id} className="p-4 hover:bg-gray-50">
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-lg ${getStatusColor(activity.status)}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                      <p className="text-sm text-gray-600">{activity.description}</p>
                      <p className="text-xs text-gray-500 mt-1">{activity.timestamp}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Health Metrics */}
        <div className="card">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Health Metrics</h2>
          </div>
          <div className="p-6 space-y-4">
            {healthMetrics.map((metric, index) => {
              const TrendIcon = getTrendIcon(metric.trend);
              return (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{metric.label}</p>
                    <p className="text-xs text-gray-600">
                      {metric.value} {metric.unit}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    {metric.change !== 0 && (
                      <div className={`flex items-center ${getTrendColor(metric.trend)}`}>
                        <TrendIcon className="h-3 w-3" />
                        <span className="text-xs font-medium">
                          {Math.abs(metric.change)}%
                        </span>
                      </div>
                    )}
                    <div className={`w-2 h-2 rounded-full ${
                      metric.status === 'normal' ? 'bg-green-500' :
                      metric.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                    }`}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">System Health</h2>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Overall Health</span>
                <span className="text-sm font-semibold text-gray-900">{stats.systemHealth}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${stats.systemHealth}%` }}
                ></div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span className="text-gray-700">Systems Operational</span>
              </div>
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-4 w-4 text-yellow-500" />
                <span className="text-gray-700">1 Warning</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">User Satisfaction</span>
              <div className="flex items-center space-x-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`h-4 w-4 ${
                      star <= Math.floor(stats.userSatisfaction / 20)
                        ? 'text-yellow-400 fill-current'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
                <span className="text-sm font-semibold text-gray-900 ml-2">
                  {stats.userSatisfaction}%
                </span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4 text-green-500" />
                <span className="text-gray-700">Response Time: 1.2s</span>
              </div>
              <div className="flex items-center space-x-2">
                <Shield className="h-4 w-4 text-blue-500" />
                <span className="text-gray-700">Security: Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
