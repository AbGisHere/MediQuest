import React, { useState, useEffect } from 'react';
import { FileText, Download, Calendar, Filter } from 'lucide-react';
import apiService from '../services/api';
import type { Vital, Alert } from '../types';

const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<string>('vitals');

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        
        // Get patients first, then fetch vitals for first patient
        const patients = await apiService.getPatientsWithConsent(0, 10);
        
        if (patients.length > 0) {
          const vitalsData = await apiService.getPatientVitals(patients[0].id, undefined, 50);
        }
        
        // Generate sample reports
        const sampleReports = [
          {
            id: '1',
            type: 'Vitals Summary',
            description: 'Comprehensive vital signs analysis',
            date: new Date().toISOString(),
            status: 'completed'
          },
          {
            id: '2', 
            type: 'Alerts Report',
            description: 'Critical alerts and notifications',
            date: new Date(Date.now() - 86400000).toISOString(),
            status: 'completed'
          },
          {
            id: '3',
            type: 'Patient Overview',
            description: 'Complete patient health profile',
            date: new Date(Date.now() - 172800000).toISOString(),
            status: 'completed'
          }
        ];
        
        setReports(sampleReports);
      } catch (error) {
        console.error('Error fetching reports:', error);
        // Set default reports on error
        setReports([
          {
            id: '1',
            type: 'System Report',
            description: 'System health and status',
            date: new Date().toISOString(),
            status: 'completed'
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  const handleDownloadReport = (reportId: string) => {
    console.log('Downloading report:', reportId);
    // In a real app, this would generate and download a PDF
    alert('Report download started!');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="text-sm text-gray-600">Generate and download comprehensive health reports</p>
        </div>
        <div className="flex space-x-3">
          <button className="btn btn-primary">
            <FileText className="h-4 w-4 mr-2" />
            Generate New Report
          </button>
          <button className="btn btn-outline">
            <Calendar className="h-4 w-4 mr-2" />
            Schedule Reports
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="flex items-center space-x-4 mb-4">
          <Filter className="h-4 w-4 text-gray-400" />
          <select 
            value={selectedReport}
            onChange={(e) => setSelectedReport(e.target.value)}
            className="border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            <option value="vitals">Vitals Reports</option>
            <option value="alerts">Alerts Reports</option>
            <option value="patients">Patient Summary</option>
            <option value="emergency">Emergency Reports</option>
          </select>
        </div>
      </div>

      {/* Reports List */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Available Reports</h3>
        
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {reports.map((report) => (
              <div key={report.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex items-center space-x-3">
                  <FileText className="h-8 w-8 text-blue-600" />
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">{report.type}</h4>
                    <p className="text-sm text-gray-600">{report.description}</p>
                    <p className="text-xs text-gray-500">
                      Generated: {new Date(report.date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    report.status === 'completed' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {report.status}
                  </span>
                  <button
                    onClick={() => handleDownloadReport(report.id)}
                    className="btn btn-outline btn-sm"
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Download
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportsPage;
