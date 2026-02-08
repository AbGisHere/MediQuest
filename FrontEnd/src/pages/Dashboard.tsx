import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';
import { Heart, Activity, Users, AlertTriangle, TrendingUp, Calendar } from 'lucide-react';
import apiService from '../services/api';
import type { Vital, Alert } from '../types';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalPatients: 0,
    totalVitals: 0,
    activeAlerts: 0,
    recentActivity: 0,
  });
  const [recentVitals, setRecentVitals] = useState<Vital[]>([]);
  const [activeAlerts, setActiveAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);

        if (user?.role !== 'patient') {
          // Fetch data for doctors/admins
          const [patients, vitals, alerts] = await Promise.all([
            apiService.getPatients(0, 10),
            apiService.getPatientVitals('dummy', undefined, 5), // This would need proper patient IDs
            apiService.getActiveEmergencyOverrides(),
          ]);

          setActiveAlerts(alerts);


          setStats({
            totalPatients: patients.length || 0,
            totalVitals: vitals.length || 0,
            activeAlerts: alerts.length || 0,
            recentActivity: 0, // Would come from audit logs
          });
        } else {
          // Fetch patient-specific data
          const vitals = await apiService.getPatientVitals('patient-id', undefined, 5);
          setRecentVitals(vitals);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  const statCards = [
    {
      title: 'Total Patients',
      value: stats.totalPatients,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%',
      changeType: 'positive',
    },
    {
      title: 'Vitals Recorded',
      value: stats.totalVitals,
      icon: Activity,
      color: 'bg-green-500',
      change: '+8%',
      changeType: 'positive',
    },
    {
      title: 'Active Alerts',
      value: stats.activeAlerts,
      icon: AlertTriangle,
      color: 'bg-red-500',
      change: '-2%',
      changeType: 'negative',
    },
    {
      title: 'Recent Activity',
      value: stats.recentActivity,
      icon: Calendar,
      color: 'bg-purple-500',
      change: '+5%',
      changeType: 'positive',
    },
  ];

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.username}!
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Here's what's happening with your medical data today.
          </p>
        </div>

        {/* Stats Grid */}
        {user?.role !== 'patient' && (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {statCards.map((stat) => {
              const Icon = stat.icon;
              return (
                <div key={stat.title} className="card p-6">
                  <div className="flex items-center">
                    <div className={`p-3 rounded-lg ${stat.color}`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                      <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <span
                      className={`text-sm font-medium ${stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                        }`}
                    >
                      {stat.change}
                    </span>
                    <span className="text-sm text-gray-500 ml-2">from last month</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Vitals */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Recent Vitals</h3>
              <Activity className="h-5 w-5 text-gray-400" />
            </div>
            <div className="space-y-3">
              {recentVitals.length > 0 ? (
                recentVitals.map((vital) => (
                  <div key={vital.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{vital.vital_type}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(vital.recorded_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">
                        {vital.value} {vital.unit}
                      </p>
                      <p className="text-xs text-gray-500">{vital.source}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">No recent vitals recorded</p>
              )}
            </div>
          </div>

          {/* Active Alerts */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Active Alerts</h3>
              <AlertTriangle className="h-5 w-5 text-gray-400" />
            </div>
            <div className="space-y-3">
              {activeAlerts.length > 0 ? (
                activeAlerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={`p-3 rounded border-l-4 ${alert.severity === 'critical'
                        ? 'bg-red-50 border-red-500'
                        : alert.severity === 'warning'
                          ? 'bg-yellow-50 border-yellow-500'
                          : 'bg-blue-50 border-blue-500'
                      }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{alert.alert_type}</p>
                        <p className="text-xs text-gray-500">{alert.message}</p>
                      </div>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${alert.severity === 'critical'
                            ? 'bg-red-100 text-red-800'
                            : alert.severity === 'warning'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}
                      >
                        {alert.severity}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">No active alerts</p>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {user?.role !== 'patient' && (
              <>
                <button className="btn btn-outline btn-md">
                  <Users className="h-4 w-4 mr-2" />
                  Add Patient
                </button>
                <button className="btn btn-outline btn-md">
                  <Activity className="h-4 w-4 mr-2" />
                  Record Vitals
                </button>
              </>
            )}
            <button className="btn btn-outline btn-md">
              <TrendingUp className="h-4 w-4 mr-2" />
              View Reports
            </button>
            <button className="btn btn-outline btn-md">
              <Heart className="h-4 w-4 mr-2" />
              Health Profile
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
