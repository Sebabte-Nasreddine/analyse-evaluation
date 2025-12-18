import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Upload, FileText, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import api from '../services/api';

export default function UploadPage() {
    const [uploadStatus, setUploadStatus] = useState(null);
    const queryClient = useQueryClient();

    const uploadMutation = useMutation({
        mutationFn: api.uploadFile,
        onSuccess: (data) => {
            setUploadStatus({
                type: 'success',
                message: `✓ Fichier traité avec succès! ${data.total_evaluations} évaluations analysées.`,
                data,
            });
            // Invalider les caches pour rafraîchir les données
            queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
            queryClient.invalidateQueries({ queryKey: ['evaluations'] });
            queryClient.invalidateQueries({ queryKey: ['themes'] });
        },
        onError: (error) => {
            setUploadStatus({
                type: 'error',
                message: `✗ Erreur lors du traitement: ${error.response?.data?.detail || error.message}`,
            });
        },
    });

    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles.length > 0) {
            const file = acceptedFiles[0];
            setUploadStatus({
                type: 'uploading',
                message: `Traitement de ${file.name}...`,
            });
            uploadMutation.mutate(file);
        }
    }, [uploadMutation]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv'],
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
            'application/vnd.ms-excel': ['.xls'],
        },
        maxFiles: 1,
        multiple: false,
    });

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div className="animate-fade-in">
                <h1 className="text-3xl font-bold text-gray-900">Upload des Évaluations</h1>
                <p className="text-gray-600 mt-1">
                    Importez vos fichiers d'évaluations pour une analyse automatique par NLP
                </p>
            </div>

            {/* Instructions */}
            <div className="card animate-fade-in">
                <div className="card-header">
                    <h2 className="text-lg font-semibold">Instructions</h2>
                </div>
                <div className="space-y-4">
                    <div>
                        <h3 className="font-medium text-gray-900 mb-2">Formats acceptés:</h3>
                        <div className="flex flex-wrap gap-2">
                            <span className="badge badge-neutral">CSV (.csv)</span>
                            <span className="badge badge-neutral">Excel (.xlsx, .xls)</span>
                            <span className="badge badge-neutral">PDF (.pdf)</span>
                        </div>
                    </div>

                    <div>
                        <h3 className="font-medium text-gray-900 mb-2">Structure requise:</h3>
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <code className="text-sm text-gray-700">
                                evaluation_id, formation_id, type_formation, formateur_id, satisfaction,
                                contenu, logistique, applicabilite, commentaire, langue, date
                            </code>
                        </div>
                        <p className="text-sm text-gray-600 mt-2">
                            Les colonnes peuvent avoir des noms légèrement différents (ex: "eval_id", "formation", etc.)
                        </p>
                    </div>

                    <div>
                        <h3 className="font-medium text-gray-900 mb-2">Langues supportées:</h3>
                        <div className="flex gap-3">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                                <span className="text-sm text-gray-700">Français (FR)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                                <span className="text-sm text-gray-700">Arabe (AR)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                                <span className="text-sm text-gray-700">Darija (DARIJA)</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Upload Zone */}
            <div className="card animate-fade-in">
                <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${isDragActive
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                        }`}
                >
                    <input {...getInputProps()} />
                    <div className="flex flex-col items-center gap-4">
                        <div className={`p-4 rounded-full ${isDragActive ? 'bg-primary-100' : 'bg-gray-100'
                            }`}>
                            <Upload className={`h-12 w-12 ${isDragActive ? 'text-primary-600' : 'text-gray-400'
                                }`} />
                        </div>
                        {isDragActive ? (
                            <p className="text-lg text-primary-600 font-medium">
                                Déposez le fichier ici...
                            </p>
                        ) : (
                            <>
                                <div>
                                    <p className="text-lg text-gray-700 font-medium">
                                        Glissez-déposez votre fichier ici
                                    </p>
                                    <p className="text-sm text-gray-500 mt-1">
                                        ou cliquez pour sélectionner un fichier
                                    </p>
                                </div>
                                <button className="btn-primary">
                                    <FileText className="h-4 w-4 mr-2" />
                                    Choisir un fichier
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* Status */}
            {uploadStatus && (
                <div className={`card animate-fade-in ${uploadStatus.type === 'success' ? 'border-l-4 border-success-500 bg-success-50' :
                        uploadStatus.type === 'error' ? 'border-l-4 border-danger-500 bg-danger-50' :
                            'border-l-4 border-primary-500 bg-primary-50'
                    }`}>
                    <div className="flex items-start gap-3">
                        {uploadStatus.type === 'success' && (
                            <CheckCircle className="h-6 w-6 text-success-600 mt-0.5" />
                        )}
                        {uploadStatus.type === 'error' && (
                            <AlertCircle className="h-6 w-6 text-danger-600 mt-0.5" />
                        )}
                        {uploadStatus.type === 'uploading' && (
                            <Loader className="h-6 w-6 text-primary-600 mt-0.5 animate-spin" />
                        )}
                        <div className="flex-1">
                            <p className={`font-medium ${uploadStatus.type === 'success' ? 'text-success-900' :
                                    uploadStatus.type === 'error' ? 'text-danger-900' :
                                        'text-primary-900'
                                }`}>
                                {uploadStatus.message}
                            </p>
                            {uploadStatus.data && (
                                <div className="mt-3 space-y-1 text-sm text-success-800">
                                    <p>📄 Fichier: {uploadStatus.data.file_name}</p>
                                    <p>📊 Évaluations traitées: {uploadStatus.data.total_evaluations}</p>
                                    <p>✨ Analyse NLP complétée (sentiment, thèmes, clustering)</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Example */}
            <div className="card animate-fade-in">
                <div className="card-header">
                    <h2 className="text-lg font-semibold">Exemple de fichier CSV</h2>
                </div>
                <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                    <pre className="text-xs">
                        {`evaluation_id,formation_id,type_formation,formateur_id,satisfaction,contenu,logistique,applicabilite,commentaire,langue,date
1,F001,Lean Six Sigma,FOR01,5,4,4,3,Formation très utile et bien structurée,FR,2024-01-05
2,F001,Lean Six Sigma,FOR01,4,4,3,3,Contenu intéressant mais trop théorique,FR,2024-01-05
3,F002,SAP,FOR02,3,3,4,4,محتوى جيد ولكن يحتاج المزيد من التطبيق,AR,2024-01-06
4,F003,Soft Skills,FOR03,5,5,5,5,Formation mezyana bezzaf,DARIJA,2024-01-07`}
                    </pre>
                </div>
            </div>
        </div>
    );
}
