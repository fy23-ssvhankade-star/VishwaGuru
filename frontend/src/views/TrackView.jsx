import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { issuesApi } from '../api/issues';
import { ArrowLeft, Search, Activity, Calendar, MapPin, CheckCircle, Clock, AlertTriangle } from 'lucide-react';

const TrackView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchId, setSearchId] = useState(id || '');
  const [issue, setIssue] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (id) {
      fetchIssue(id);
    }
  }, [id]);

  const fetchIssue = async (issueId) => {
    setLoading(true);
    setError(null);
    setIssue(null);
    try {
      const data = await issuesApi.getIssue(issueId);
      setIssue(data);
    } catch (err) {
      setError("Issue not found or server error.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchId) {
      navigate(`/track/${searchId}`);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved': return 'text-green-600 bg-green-50 border-green-200';
      case 'verified': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'in_progress': return 'text-purple-600 bg-purple-50 border-purple-200';
      case 'open': return 'text-orange-600 bg-orange-50 border-orange-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="p-4 max-w-2xl mx-auto pb-20">
      <div className="flex items-center mb-6">
        <button onClick={() => navigate('/')} className="mr-4 p-2 rounded-full hover:bg-gray-100">
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-2xl font-bold">Track Issue</h1>
      </div>

      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex gap-2">
          <input
            type="number"
            placeholder="Enter Issue ID (e.g. 1)"
            className="flex-1 p-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 outline-none"
            value={searchId}
            onChange={(e) => setSearchId(e.target.value)}
          />
          <button type="submit" className="bg-blue-600 text-white p-3 rounded-lg font-bold flex items-center gap-2 hover:bg-blue-700 transition">
            <Search size={20} />
            Track
          </button>
        </div>
      </form>

      {loading && (
        <div className="text-center py-10">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Fetching issue details...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-center gap-3">
          <AlertTriangle size={24} />
          <p>{error}</p>
        </div>
      )}

      {issue && (
        <div className="space-y-6 animate-fade-in">
          {/* Status Card */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Issue #{issue.id}</h2>
                <p className="text-sm text-gray-500">Reference: {issue.reference_id || 'N/A'}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-bold border ${getStatusColor(issue.status)} uppercase`}>
                {issue.status}
              </span>
            </div>

            <div className="flex items-center gap-2 text-gray-600 mb-2">
                <MapPin size={16} />
                <span className="text-sm">{issue.location || 'Location not available'}</span>
            </div>

            <p className="text-gray-800 text-lg mb-4">{issue.description}</p>

            {issue.image_path && (
                <div className="rounded-lg overflow-hidden border border-gray-200 mb-4">
                    <div className="bg-gray-100 p-4 text-center text-gray-500 text-sm">
                        [Image Evidence Uploaded]
                    </div>
                </div>
            )}
          </div>

          {/* Timeline */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Activity size={20} className="text-blue-600" />
                Activity Timeline
            </h3>

            <div className="space-y-4 relative pl-4 border-l-2 border-gray-100">
                <div className="relative">
                    <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-blue-600 border-2 border-white shadow-sm"></div>
                    <p className="text-sm font-bold text-gray-900">Issue Reported</p>
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                        <Calendar size={12} /> {new Date(issue.created_at).toLocaleString()}
                    </p>
                </div>

                {issue.verified_at && (
                    <div className="relative">
                        <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-purple-600 border-2 border-white shadow-sm"></div>
                        <p className="text-sm font-bold text-gray-900">Verified by Community/AI</p>
                        <p className="text-xs text-gray-500 flex items-center gap-1">
                            <CheckCircle size={12} /> {new Date(issue.verified_at).toLocaleString()}
                        </p>
                    </div>
                )}

                {issue.assigned_at && (
                    <div className="relative">
                        <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-orange-600 border-2 border-white shadow-sm"></div>
                        <p className="text-sm font-bold text-gray-900">Assigned to Authority</p>
                        <p className="text-xs text-gray-500 flex items-center gap-1">
                            <Clock size={12} /> {new Date(issue.assigned_at).toLocaleString()}
                        </p>
                        {issue.assigned_to && <p className="text-xs text-gray-600 mt-1">Assignee: {issue.assigned_to}</p>}
                    </div>
                )}

                {issue.resolved_at && (
                    <div className="relative">
                        <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-green-600 border-2 border-white shadow-sm"></div>
                        <p className="text-sm font-bold text-gray-900">Issue Resolved</p>
                        <p className="text-xs text-gray-500 flex items-center gap-1">
                            <CheckCircle size={12} /> {new Date(issue.resolved_at).toLocaleString()}
                        </p>
                    </div>
                )}
            </div>
          </div>

          {/* Action Plan */}
          {issue.action_plan && (
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-xl shadow-sm border border-blue-100">
                  <h3 className="font-bold text-blue-900 mb-2">Recommended Action Plan</h3>
                  <div className="text-sm text-blue-800 space-y-2">
                      {issue.action_plan.email_subject && (
                          <p><strong>Email:</strong> {issue.action_plan.email_subject}</p>
                      )}
                      {issue.action_plan.whatsapp && (
                          <p><strong>WhatsApp:</strong> {issue.action_plan.whatsapp}</p>
                      )}
                  </div>
              </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TrackView;
