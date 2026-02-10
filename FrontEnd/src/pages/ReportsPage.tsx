import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  Calendar, 
  Filter, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Users, 
  Heart, 
  Activity,
  BarChart3,
  PieChart,
  LineChart,
  Clock,
  Search,
  ChevronDown,
  Eye,
  Share2,
  Printer
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';

interface ReportData {
  id: string;
  title: string;
  description: string;
  type: 'vitals' | 'blood_reports' | 'alerts' | 'analytics' | 'patient_summary';
  date: string;
  status: 'completed' | 'processing' | 'scheduled';
  patientCount?: number;
  insights?: string[];
  metrics?: {
    total: number;
    normal: number;
    abnormal: number;
    critical: number;
  };
}

interface PatientAnalytics {
  totalPatients: number;
  activePatients: number;
  criticalAlerts: number;
  pendingReports: number;
  recentActivity: Array<{
    patient: string;
    action: string;
    time: string;
  }>;
}

const ReportsPage: React.FC = () => {
  const { user } = useAuth();
  const [reports, setReports] = useState<ReportData[]>([]);
  const [analytics, setAnalytics] = useState<PatientAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [dateRange, setDateRange] = useState('30days');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedReportDetail, setSelectedReportDetail] = useState<ReportData | null>(null);
  const [showReportModal, setShowReportModal] = useState(false);

  useEffect(() => {
    const fetchReportsData = async () => {
      try {
        setLoading(true);
        
        // Fetch patients and generate comprehensive reports
        const patients = await apiService.getPatientsWithConsent(0, 50);
        
        // Generate sample analytics data
        const sampleAnalytics: PatientAnalytics = {
          totalPatients: patients.length,
          activePatients: Math.floor(patients.length * 0.8),
          criticalAlerts: 3,
          pendingReports: 5,
          recentActivity: [
            { patient: 'John Doe', action: 'Blood report uploaded', time: '2 hours ago' },
            { patient: 'Sarah Johnson', action: 'Vitals updated', time: '4 hours ago' },
            { patient: 'Michael Williams', action: 'Alert triggered', time: '6 hours ago' },
            { patient: 'Emily Davis', action: 'Report generated', time: '8 hours ago' },
            { patient: 'Robert Brown', action: 'Lab results received', time: '12 hours ago' }
          ]
        };
        
        setAnalytics(sampleAnalytics);
        
        // Generate comprehensive reports with realistic timestamps
        const now = new Date();
        const sampleReports: ReportData[] = [
          {
            id: '1',
            title: 'Patient Vitals Summary',
            description: 'Comprehensive analysis of all patient vital signs across the last 30 days',
            type: 'vitals',
            date: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
            status: 'completed',
            patientCount: patients.length,
            insights: [
              '15% improvement in average blood pressure readings',
              '3 patients showing abnormal heart rate patterns',
              'Overall glucose levels within normal range'
            ],
            metrics: {
              total: patients.length * 12, // Average 12 vitals per patient
              normal: Math.floor(patients.length * 10),
              abnormal: Math.floor(patients.length * 1.5),
              critical: Math.floor(patients.length * 0.5)
            }
          },
          {
            id: '2',
            title: 'Blood Reports Analysis',
            description: 'Complete blood work analysis with trend identification and abnormality detection',
            type: 'blood_reports',
            date: new Date(now.getTime() - 6 * 60 * 60 * 1000).toISOString(), // 6 hours ago
            status: 'completed',
            patientCount: Math.floor(patients.length * 0.6),
            insights: [
              '8 patients with elevated cholesterol levels',
              '2 patients showing anemic patterns',
              'Kidney function normal across all tested patients'
            ],
            metrics: {
              total: Math.floor(patients.length * 8),
              normal: Math.floor(patients.length * 6),
              abnormal: Math.floor(patients.length * 1.8),
              critical: Math.floor(patients.length * 0.2)
            }
          },
          {
            id: '3',
            title: 'Critical Alerts Report',
            description: 'Summary of all critical alerts and emergency notifications',
            type: 'alerts',
            date: new Date(now.getTime() - 12 * 60 * 60 * 1000).toISOString(), // 12 hours ago
            status: 'completed',
            patientCount: 3,
            insights: [
              '3 critical alerts requiring immediate attention',
              '2 patients with abnormal vitals trends',
              '1 medication interaction alert'
            ],
            metrics: {
              total: 3,
              normal: 0,
              abnormal: 2,
              critical: 3
            }
          },
          {
            id: '4',
            title: 'Patient Health Analytics',
            description: 'Statistical analysis of patient health trends and outcomes',
            type: 'analytics',
            date: new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString(), // 24 hours ago
            status: 'completed',
            patientCount: patients.length,
            insights: [
              'Overall patient health score: 7.8/10',
              '20% improvement in chronic disease management',
              'Patient satisfaction rate: 92%'
            ],
            metrics: {
              total: patients.length,
              normal: Math.floor(patients.length * 0.7),
              abnormal: Math.floor(patients.length * 0.25),
              critical: Math.floor(patients.length * 0.05)
            }
          },
          {
            id: '5',
            title: 'Monthly Patient Summary',
            description: 'Comprehensive monthly overview of all patient activities and health metrics',
            type: 'patient_summary',
            date: new Date(now.getTime() - 48 * 60 * 60 * 1000).toISOString(), // 48 hours ago
            status: 'processing',
            patientCount: patients.length,
            insights: [
              'Report generation in progress...',
              'Expected completion in 5 minutes'
            ],
            metrics: {
              total: patients.length,
              normal: 0,
              abnormal: 0,
              critical: 0
            }
          }
        ];
        
        setReports(sampleReports);
      } catch (error) {
        console.error('Error fetching reports:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchReportsData();
  }, []);

  const filteredReports = reports.filter(report => {
    const matchesSearch = report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedReport === 'all' || report.type === selectedReport;
    return matchesSearch && matchesType;
  });

  const getReportIcon = (type: string) => {
    switch (type) {
      case 'vitals': return Heart;
      case 'blood_reports': return FileText;
      case 'alerts': return AlertTriangle;
      case 'analytics': return BarChart3;
      case 'patient_summary': return Users;
      default: return FileText;
    }
  };

  const getReportTypeColor = (type: string) => {
    switch (type) {
      case 'vitals': return 'bg-red-100 text-red-800 border-red-200';
      case 'blood_reports': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'alerts': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'analytics': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'patient_summary': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
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
          <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="mt-1 text-sm text-gray-600">Comprehensive health reports and patient analytics</p>
        </div>
        <div className="flex space-x-3">
          <button className="btn btn-primary">
            <Download className="h-4 w-4 mr-2" />
            Export All
          </button>
          <button className="btn btn-outline">
            <Printer className="h-4 w-4 mr-2" />
            Print
          </button>
        </div>
      </div>

      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Patients</p>
                <p className="text-2xl font-bold text-gray-900">{analytics.totalPatients}</p>
              </div>
            </div>
          </div>
          
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
                <Heart className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Patients</p>
                <p className="text-2xl font-bold text-gray-900">{analytics.activePatients}</p>
              </div>
            </div>
          </div>
          
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-red-100 rounded-lg p-3">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Critical Alerts</p>
                <p className="text-2xl font-bold text-gray-900">{analytics.criticalAlerts}</p>
              </div>
            </div>
          </div>
          
          <div className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-100 rounded-lg p-3">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending Reports</p>
                <p className="text-2xl font-bold text-gray-900">{analytics.pendingReports}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="card p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search reports..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-full"
              />
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <select
              value={selectedReport}
              onChange={(e) => setSelectedReport(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All Reports</option>
              <option value="vitals">Vitals</option>
              <option value="blood_reports">Blood Reports</option>
              <option value="alerts">Alerts</option>
              <option value="analytics">Analytics</option>
              <option value="patient_summary">Patient Summary</option>
            </select>
            
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="7days">Last 7 Days</option>
              <option value="30days">Last 30 Days</option>
              <option value="90days">Last 90 Days</option>
              <option value="1year">Last Year</option>
            </select>
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn btn-outline"
            >
              <Filter className="h-4 w-4 mr-2" />
              Filters
            </button>
          </div>
        </div>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredReports.map((report) => {
          const Icon = getReportIcon(report.type);
          
          return (
            <div key={report.id} className="card hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${getReportTypeColor(report.type)}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{report.title}</h3>
                      <p className="text-sm text-gray-600">{report.description}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(report.status)}`}>
                    {report.status}
                  </span>
                </div>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">
                      <Calendar className="h-4 w-4 inline mr-1" />
                      {formatDate(report.date)}
                    </span>
                    {report.patientCount && (
                      <span className="text-gray-600">
                        <Users className="h-4 w-4 inline mr-1" />
                        {report.patientCount} patients
                      </span>
                    )}
                  </div>
                  
                  {report.metrics && (
                    <div className="grid grid-cols-4 gap-2 text-center">
                      <div className="bg-gray-50 rounded p-2">
                        <p className="text-xs text-gray-600">Total</p>
                        <p className="text-sm font-semibold text-gray-900">{report.metrics.total}</p>
                      </div>
                      <div className="bg-green-50 rounded p-2">
                        <p className="text-xs text-green-600">Normal</p>
                        <p className="text-sm font-semibold text-green-900">{report.metrics.normal}</p>
                      </div>
                      <div className="bg-yellow-50 rounded p-2">
                        <p className="text-xs text-yellow-600">Abnormal</p>
                        <p className="text-sm font-semibold text-yellow-900">{report.metrics.abnormal}</p>
                      </div>
                      <div className="bg-red-50 rounded p-2">
                        <p className="text-xs text-red-600">Critical</p>
                        <p className="text-sm font-semibold text-red-900">{report.metrics.critical}</p>
                      </div>
                    </div>
                  )}
                  
                  {report.insights && (
                    <div className="border-t pt-3">
                      <p className="text-sm font-medium text-gray-700 mb-2">Key Insights:</p>
                      <ul className="space-y-1">
                        {report.insights.map((insight, index) => (
                          <li key={index} className="text-xs text-gray-600 flex items-start">
                            <CheckCircle className="h-3 w-3 text-green-500 mr-1 mt-0.5 flex-shrink-0" />
                            {insight}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center justify-between mt-6 pt-4 border-t">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setSelectedReportDetail(report);
                        setShowReportModal(true);
                      }}
                      className="btn btn-outline btn-sm"
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </button>
                    <button className="btn btn-outline btn-sm">
                      <Download className="h-4 w-4 mr-1" />
                      Export
                    </button>
                  </div>
                  <button className="btn btn-outline btn-sm">
                    <Share2 className="h-4 w-4 mr-1" />
                    Share
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Activity */}
      {analytics && (
        <div className="card">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {analytics.recentActivity.map((activity, index) => (
              <div key={index} className="p-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <Activity className="h-5 w-5 text-gray-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{activity.patient}</p>
                    <p className="text-sm text-gray-600">{activity.action}</p>
                  </div>
                </div>
                <span className="text-xs text-gray-500">{activity.time}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Report Detail Modal */}
      {showReportModal && selectedReportDetail && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${getReportTypeColor(selectedReportDetail.type)}`}>
                    {(() => {
                      const Icon = getReportIcon(selectedReportDetail.type);
                      return <Icon className="h-5 w-5" />;
                    })()}
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{selectedReportDetail.title}</h2>
                    <p className="text-sm text-gray-600">{selectedReportDetail.description}</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowReportModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
            </div>
            
            <div className="p-6">
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Report Details</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Type:</span>
                        <span className="text-sm font-medium">{selectedReportDetail.type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Status:</span>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(selectedReportDetail.status)}`}>
                          {selectedReportDetail.status}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Generated:</span>
                        <span className="text-sm font-medium">{formatDate(selectedReportDetail.date)}</span>
                      </div>
                      {selectedReportDetail.patientCount && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Patients:</span>
                          <span className="text-sm font-medium">{selectedReportDetail.patientCount}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {selectedReportDetail.metrics && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-3">Metrics Summary</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Total Records:</span>
                          <span className="text-sm font-medium">{selectedReportDetail.metrics.total}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Normal:</span>
                          <span className="text-sm font-medium text-green-600">{selectedReportDetail.metrics.normal}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Abnormal:</span>
                          <span className="text-sm font-medium text-yellow-600">{selectedReportDetail.metrics.abnormal}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Critical:</span>
                          <span className="text-sm font-medium text-red-600">{selectedReportDetail.metrics.critical}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                {selectedReportDetail.insights && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Key Insights</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <ul className="space-y-2">
                        {selectedReportDetail.insights.map((insight, index) => (
                          <li key={index} className="text-sm text-gray-700 flex items-start">
                            <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                            {insight}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
                
                <div className="flex justify-end space-x-3 pt-4 border-t">
                  <button className="btn btn-outline">
                    <Download className="h-4 w-4 mr-2" />
                    Download Report
                  </button>
                  <button className="btn btn-outline">
                    <Share2 className="h-4 w-4 mr-2" />
                    Share Report
                  </button>
                  <button className="btn btn-primary">
                    <Printer className="h-4 w-4 mr-2" />
                    Print Report
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportsPage;
