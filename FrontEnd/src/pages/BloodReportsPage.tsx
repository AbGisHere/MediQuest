import React, { useState, useEffect } from 'react';
import { FileText, Download, Eye, CheckCircle, Plus, AlertTriangle, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';

interface BloodReport {
  id: string;
  patient_id: string;
  patient_name?: string;
  uploaded_by: string;
  uploader_name?: string;
  report_type: string;
  test_date?: string;
  lab_name?: string;
  // CBC Values
  hemoglobin?: number;
  wbc_count?: number;
  rbc_count?: number;
  platelet_count?: number;
  hematocrit?: number;
  mcv?: number;
  mch?: number;
  mchc?: number;
  // Glucose
  glucose_fasting?: number;
  glucose_random?: number;
  glucose_pp?: number;
  hba1c?: number;
  // Lipid Panel
  cholesterol_total?: number;
  cholesterol_hdl?: number;
  cholesterol_ldl?: number;
  cholesterol_vldl?: number;
  triglycerides?: number;
  // Liver Function
  sgot?: number;
  sgpt?: number;
  alkaline_phosphatase?: number;
  bilirubin_total?: number;
  bilirubin_direct?: number;
  bilirubin_indirect?: number;
  total_protein?: number;
  albumin?: number;
  globulin?: number;
  // Kidney Function
  creatinine?: number;
  urea?: number;
  uric_acid?: number;
  bun?: number;
  egfr?: number;
  // Thyroid
  tsh?: number;
  t3?: number;
  t4?: number;
  // Electrolytes
  sodium?: number;
  potassium?: number;
  chloride?: number;
  // Minerals
  calcium?: number;
  phosphorus?: number;
  magnesium?: number;
  iron?: number;
  vitamin_d?: number;
  vitamin_b12?: number;
  // Metadata
  parsing_confidence?: number;
  uploaded_at: string;
  updated_at: string;
}

const BloodReportsPage: React.FC = () => {
  const { user } = useAuth();
  const [reports, setReports] = useState<BloodReport[]>([]);
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPatient, setSelectedPatient] = useState<string>('');
  const [selectedReport, setSelectedReport] = useState<BloodReport | null>(null);
  const [showReportDetail, setShowReportDetail] = useState(false);
  const [detailedReport, setDetailedReport] = useState<BloodReport | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    testDate: '',
    labName: ''
  });

  useEffect(() => {
    const fetchPatients = async () => {
      if (user?.role !== 'patient') {
        try {
          const patientsData = await apiService.getPatientsWithConsent(0, 50);
          setPatients(patientsData);
          if (patientsData.length > 0 && !selectedPatient) {
            setSelectedPatient(patientsData[0].id);
          }
        } catch (error) {
          console.error('Error fetching patients:', error);
          setPatients([]);
        }
      }
    };

    fetchPatients();
  }, [user, selectedPatient]);

  useEffect(() => {
    const fetchReports = async () => {
      if (!selectedPatient) return;

      try {
        setLoading(true);
        const reportsData = await apiService.getPatientBloodReports(selectedPatient);

        // Add patient names to reports
        const reportsWithNames = reportsData.map((report: any) => {
          const patient = patients.find(p => p.id === report.patient_id);
          return {
            ...report,
            patient_name: patient ? `${patient.first_name} ${patient.last_name}` : 'Unknown Patient'
          };
        });

        setReports(reportsWithNames);
      } catch (error) {
        console.error('Error fetching blood reports:', error);
        setReports([]);
      } finally {
        setLoading(false);
      }
    };

    if (selectedPatient) {
      fetchReports();
    }
  }, [user, selectedPatient, patients]);

  const fetchDetailedReport = async (reportId: string) => {
    try {
      setLoadingDetail(true);
      const detailedData = await apiService.getBloodReport(reportId);
      setDetailedReport(detailedData);
    } catch (error) {
      console.error('Error fetching detailed report:', error);
    } finally {
      setLoadingDetail(false);
    }
  };

  const getNormalRange = (test: string, value: number) => {
    const ranges: { [key: string]: { min: number; max: number; unit: string } } = {
      hemoglobin: { min: 12, max: 16, unit: 'g/dL' },
      wbc_count: { min: 4000, max: 11000, unit: 'cells/μL' },
      rbc_count: { min: 4.2, max: 5.4, unit: 'million cells/μL' },
      platelet_count: { min: 150000, max: 450000, unit: 'cells/μL' },
      glucose_fasting: { min: 70, max: 100, unit: 'mg/dL' },
      hba1c: { min: 4, max: 5.7, unit: '%' },
      cholesterol_total: { min: 0, max: 200, unit: 'mg/dL' },
      cholesterol_ldl: { min: 0, max: 100, unit: 'mg/dL' },
      triglycerides: { min: 0, max: 150, unit: 'mg/dL' }
    };

    const range = ranges[test];
    if (!range) return { status: 'normal', color: 'text-green-600' };

    if (value < range.min) return { status: 'low', color: 'text-blue-600' };
    if (value > range.max) return { status: 'high', color: 'text-red-600' };
    return { status: 'normal', color: 'text-green-600' };
  };

  const roundToTwo = (value: number): number => {
    return Math.round(value * 100) / 100;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'low': return AlertTriangle;
      case 'high': return AlertTriangle;
      default: return CheckCircle;
    }
  };

  const getReportTypeColor = (type: string) => {
    switch (type) {
      case 'cbc': return 'bg-purple-100 text-purple-800';
      case 'lipid_panel': return 'bg-orange-100 text-orange-800';
      case 'liver_function': return 'bg-yellow-100 text-yellow-800';
      case 'kidney_function': return 'bg-blue-100 text-blue-800';
      case 'thyroid': return 'bg-indigo-100 text-indigo-800';
      case 'diabetes': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatValue = (value?: number, unit?: string) => {
    if (value === undefined || value === null) return 'N/A';
    return `${roundToTwo(value)} ${unit || ''}`;
  };

  const renderLabSection = (title: string, tests: { name: string; value?: number; unit?: string }[]) => {
    const availableTests = tests.filter(test => test.value !== undefined && test.value !== null);

    if (availableTests.length === 0) {
      return null;
    }

    return (
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">{title}</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {availableTests.map((test, index) => (
            <div key={index} className="flex justify-between items-center">
              <span className="text-sm text-gray-600">{test.name}</span>
              <span className="text-sm font-medium text-gray-900">
                {formatValue(test.value, test.unit)}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadFile(file);
    }
  };

  const handleUpload = async () => {
    if (!uploadFile || !selectedPatient) {
      alert('Please select a file and patient');
      return;
    }

    try {
      setUploading(true);
      await apiService.uploadBloodReport(
        selectedPatient,
        uploadFile,
        uploadForm.testDate || undefined,
        uploadForm.labName || undefined
      );
      
      // Refresh reports list
      const reportsData = await apiService.getPatientBloodReports(selectedPatient);
      setReports(reportsData);
      
      // Reset form
      setUploadFile(null);
      setUploadForm({ testDate: '', labName: '' });
      setShowUploadModal(false);
      
      alert('Report uploaded successfully!');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload report. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Blood Reports</h1>
          <p className="mt-1 text-sm text-gray-600">Comprehensive laboratory test results and analysis</p>
        </div>
        <div className="flex space-x-3">
          {user?.role === 'admin' && (
            <button 
              onClick={() => setShowUploadModal(true)}
              className="btn btn-primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              Upload Report
            </button>
          )}
          <button className="btn btn-outline">
            <Download className="h-4 w-4 mr-2" />
            Export Data
          </button>
        </div>
      </div>

      {/* Patient Selection */}
      {user?.role !== 'patient' && (
        <div className="card p-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Patient:</label>
            <select
              value={selectedPatient}
              onChange={(e) => setSelectedPatient(e.target.value)}
              className="border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500 min-w-[200px]"
            >
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.first_name} {patient.last_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Reports List */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Laboratory Reports</h3>
        </div>

        {reports.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {reports.map((report) => (
              <div key={report.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className={`px-3 py-1 text-xs font-medium rounded-full ${getReportTypeColor(report.report_type)}`}>
                        {report.report_type.toUpperCase()}
                      </span>
                      <h4 className="text-lg font-semibold text-gray-900">
                        {report.test_date ? new Date(report.test_date).toLocaleDateString() : 'No Date'}
                      </h4>
                    </div>

                    <div className="text-sm text-gray-600 mb-2">
                      <p>Lab: {report.lab_name || 'Unknown Lab'}</p>
                      <p>Patient: {report.patient_name}</p>
                      <p>Uploaded by: {report.uploader_name || 'Unknown'} on {new Date(report.uploaded_at).toLocaleDateString()}</p>
                    </div>

                    {/* Key Values Preview */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mt-4">
                      {report.hemoglobin && (
                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                          <p className="text-xs text-gray-600">Hemoglobin</p>
                          <p className="text-lg font-bold text-gray-900">{formatValue(report.hemoglobin, 'g/dL')}</p>
                        </div>
                      )}
                      {report.cholesterol_total && (
                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                          <p className="text-xs text-gray-600">Total Cholesterol</p>
                          <p className="text-lg font-bold text-gray-900">{formatValue(report.cholesterol_total, 'mg/dL')}</p>
                        </div>
                      )}
                      {report.glucose_fasting && (
                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                          <p className="text-xs text-gray-600">Fasting Glucose</p>
                          <p className="text-lg font-bold text-gray-900">{formatValue(report.glucose_fasting, 'mg/dL')}</p>
                        </div>
                      )}
                      {report.creatinine && (
                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                          <p className="text-xs text-gray-600">Creatinine</p>
                          <p className="text-lg font-bold text-gray-900">{formatValue(report.creatinine, 'mg/dL')}</p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 ml-6">
                    <button
                      onClick={() => {
                        setSelectedReport(report);
                        setShowReportDetail(true);
                        fetchDetailedReport(report.id);
                      }}
                      className="btn btn-outline btn-sm"
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View Details
                    </button>
                    {user?.role === 'admin' && (
                      <button className="btn btn-outline btn-sm">
                        <Download className="h-4 w-4 mr-1" />
                        Download PDF
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">No blood reports found</p>
            <p className="text-sm text-gray-500">
              {selectedPatient ? 'No laboratory reports have been uploaded for this patient yet.' : 'Select a patient to view their blood reports.'}
            </p>
          </div>
        )}
      </div>

      {/* Report Detail Modal */}
      {showReportDetail && selectedReport && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Blood Report Details</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    {detailedReport?.patient_name || selectedReport?.patient_name} - {detailedReport?.test_date ? new Date(detailedReport.test_date).toLocaleDateString() : selectedReport?.test_date ? new Date(selectedReport.test_date).toLocaleDateString() : 'No Date'}
                  </p>
                </div>
                <button
                  onClick={() => setShowReportDetail(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              {loadingDetail ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                  <p className="text-gray-600 mt-4">Loading detailed report...</p>
                </div>
              ) : (
                <div className="p-6">
                  {/* Report Metadata */}
                  <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Report Information</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Lab Name:</p>
                        <p className="font-medium text-gray-900">{detailedReport?.lab_name || selectedReport?.lab_name || 'Unknown'}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Report Type:</p>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getReportTypeColor(detailedReport?.report_type || selectedReport?.report_type)}`}>
                          {(detailedReport?.report_type || selectedReport?.report_type || '').toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="text-gray-600">Test Date:</p>
                        <p className="font-medium text-gray-900">
                          {detailedReport?.test_date ? new Date(detailedReport.test_date).toLocaleDateString() : selectedReport?.test_date ? new Date(selectedReport.test_date).toLocaleDateString() : 'Not specified'}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Parsing Confidence:</p>
                        <p className="font-medium text-gray-900">
                          {detailedReport?.parsing_confidence ? `${roundToTwo(detailedReport.parsing_confidence)}%` : selectedReport?.parsing_confidence ? `${roundToTwo(selectedReport.parsing_confidence)}%` : 'N/A'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* CBC Values */}
                  {(detailedReport?.hemoglobin || detailedReport?.wbc_count || detailedReport?.rbc_count || detailedReport?.platelet_count) && (
                    renderLabSection('Complete Blood Count (CBC)', [
                      { name: 'Hemoglobin', value: detailedReport.hemoglobin, unit: 'g/dL' },
                      { name: 'WBC Count', value: detailedReport.wbc_count, unit: 'cells/μL' },
                      { name: 'RBC Count', value: detailedReport.rbc_count, unit: 'million cells/μL' },
                      { name: 'Platelets', value: detailedReport.platelet_count, unit: 'cells/μL' },
                      { name: 'Hematocrit', value: detailedReport.hematocrit, unit: '%' },
                      { name: 'MCV', value: detailedReport.mcv, unit: 'fL' },
                      { name: 'MCH', value: detailedReport.mch, unit: 'pg' },
                      { name: 'MCHC', value: detailedReport.mchc, unit: 'g/dL' }
                    ])
                  )}

                  {/* Glucose Panel */}
                  {(detailedReport?.glucose_fasting || detailedReport?.glucose_random || detailedReport?.glucose_pp || detailedReport?.hba1c) && (
                    renderLabSection('Glucose Panel', [
                      { name: 'Fasting Glucose', value: detailedReport.glucose_fasting, unit: 'mg/dL' },
                      { name: 'Random Glucose', value: detailedReport.glucose_random, unit: 'mg/dL' },
                      { name: 'Post-Prandial', value: detailedReport.glucose_pp, unit: 'mg/dL' },
                      { name: 'HbA1c', value: detailedReport.hba1c, unit: '%' }
                    ])
                  )}

                  {/* Lipid Panel */}
                  {(detailedReport?.cholesterol_total || detailedReport?.cholesterol_hdl || detailedReport?.cholesterol_ldl || detailedReport?.triglycerides) && (
                    renderLabSection('Lipid Panel', [
                      { name: 'Total Cholesterol', value: detailedReport.cholesterol_total, unit: 'mg/dL' },
                      { name: 'HDL Cholesterol', value: detailedReport.cholesterol_hdl, unit: 'mg/dL' },
                      { name: 'LDL Cholesterol', value: detailedReport.cholesterol_ldl, unit: 'mg/dL' },
                      { name: 'VLDL Cholesterol', value: detailedReport.cholesterol_vldl, unit: 'mg/dL' },
                      { name: 'Triglycerides', value: detailedReport.triglycerides, unit: 'mg/dL' }
                    ])
                  )}

                  {/* Liver Function */}
                  {(detailedReport?.sgot || detailedReport?.sgpt || detailedReport?.alkaline_phosphatase || detailedReport?.bilirubin_total) && (
                    renderLabSection('Liver Function Tests', [
                      { name: 'SGOT (AST)', value: detailedReport.sgot, unit: 'U/L' },
                      { name: 'SGPT (ALT)', value: detailedReport.sgpt, unit: 'U/L' },
                      { name: 'Alkaline Phosphatase', value: detailedReport.alkaline_phosphatase, unit: 'U/L' },
                      { name: 'Total Bilirubin', value: detailedReport.bilirubin_total, unit: 'mg/dL' },
                      { name: 'Direct Bilirubin', value: detailedReport.bilirubin_direct, unit: 'mg/dL' },
                      { name: 'Indirect Bilirubin', value: detailedReport.bilirubin_indirect, unit: 'mg/dL' },
                      { name: 'Total Protein', value: detailedReport.total_protein, unit: 'g/dL' },
                      { name: 'Albumin', value: detailedReport.albumin, unit: 'g/dL' },
                      { name: 'Globulin', value: detailedReport.globulin, unit: 'g/dL' }
                    ])
                  )}

                  {/* Kidney Function */}
                  {(detailedReport?.creatinine || detailedReport?.urea || detailedReport?.bun || detailedReport?.egfr) && (
                    renderLabSection('Kidney Function Tests', [
                      { name: 'Creatinine', value: detailedReport.creatinine, unit: 'mg/dL' },
                      { name: 'Urea', value: detailedReport.urea, unit: 'mg/dL' },
                      { name: 'BUN', value: detailedReport.bun, unit: 'mg/dL' },
                      { name: 'eGFR', value: detailedReport.egfr, unit: 'mL/min/1.73m²' }
                    ])
                  )}

                  {/* Thyroid Function */}
                  {(detailedReport?.tsh || detailedReport?.t3 || detailedReport?.t4) && (
                    renderLabSection('Thyroid Function Tests', [
                      { name: 'TSH', value: detailedReport.tsh, unit: 'μIU/mL' },
                      { name: 'T3', value: detailedReport.t3, unit: 'ng/dL' },
                      { name: 'T4', value: detailedReport.t4, unit: 'μg/dL' }
                    ])
                  )}

                  {/* Electrolytes */}
                  {(detailedReport?.sodium || detailedReport?.potassium || detailedReport?.chloride) && (
                    renderLabSection('Electrolytes', [
                      { name: 'Sodium', value: detailedReport.sodium, unit: 'mEq/L' },
                      { name: 'Potassium', value: detailedReport.potassium, unit: 'mEq/L' },
                      { name: 'Chloride', value: detailedReport.chloride, unit: 'mEq/L' }
                    ])
                  )}

                  {/* Minerals & Vitamins */}
                  {(detailedReport?.calcium || detailedReport?.iron || detailedReport?.vitamin_d || detailedReport?.vitamin_b12) && (
                    renderLabSection('Minerals & Vitamins', [
                      { name: 'Calcium', value: detailedReport.calcium, unit: 'mg/dL' },
                      { name: 'Phosphorus', value: detailedReport.phosphorus, unit: 'mg/dL' },
                      { name: 'Magnesium', value: detailedReport.magnesium, unit: 'mg/dL' },
                      { name: 'Iron', value: detailedReport.iron, unit: 'μg/dL' },
                      { name: 'Vitamin D', value: detailedReport.vitamin_d, unit: 'ng/mL' },
                      { name: 'Vitamin B12', value: detailedReport.vitamin_b12, unit: 'pg/mL' }
                    ])
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Upload Report Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Upload Blood Report</h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Patient</label>
                <select
                  value={selectedPatient}
                  onChange={(e) => setSelectedPatient(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="">Select a patient</option>
                  {patients.map((patient) => (
                    <option key={patient.id} value={patient.id}>
                      {patient.first_name} {patient.last_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Test Date (Optional)</label>
                <input
                  type="date"
                  value={uploadForm.testDate}
                  onChange={(e) => setUploadForm({ ...uploadForm, testDate: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Lab Name (Optional)</label>
                <input
                  type="text"
                  value={uploadForm.labName}
                  onChange={(e) => setUploadForm({ ...uploadForm, labName: e.target.value })}
                  placeholder="Enter lab name"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Select File</label>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={handleFileSelect}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                {uploadFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    Selected: {uploadFile.name}
                  </p>
                )}
              </div>
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                onClick={() => setShowUploadModal(false)}
                className="flex-1 btn btn-outline"
              >
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={uploading || !uploadFile || !selectedPatient}
                className="flex-1 btn btn-primary"
              >
                {uploading ? 'Uploading...' : 'Upload Report'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BloodReportsPage;
