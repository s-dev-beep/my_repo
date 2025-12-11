'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  ArrowLeft, Upload, FileSpreadsheet, Download, CheckCircle2, 
  AlertCircle, Table, FileText, X
} from 'lucide-react'
import { Progress } from '@/components/ui/progress'

const fieldMappings = [
  { csvField: 'Name', crmField: 'name', required: true },
  { csvField: 'Email', crmField: 'email', required: false },
  { csvField: 'Phone', crmField: 'phone', required: true },
  { csvField: 'Source', crmField: 'source', required: false },
  { csvField: 'Budget', crmField: 'budget', required: false },
  { csvField: 'Location', crmField: 'preferredLocation', required: false },
]

const crmFields = ['name', 'email', 'phone', 'source', 'budget', 'preferredLocation', 'propertyType', 'notes', 'assignedTo']

export default function ImportLeadsPage() {
  const [step, setStep] = useState(1)
  const [file, setFile] = useState<File | null>(null)
  const [importing, setImporting] = useState(false)
  const [progress, setProgress] = useState(0)
  const [mappings, setMappings] = useState(fieldMappings)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = () => {
    if (file) {
      setStep(2)
    }
  }

  const handleImport = async () => {
    setImporting(true)
    // Simulate import progress
    for (let i = 0; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 300))
      setProgress(i)
    }
    setStep(3)
    setImporting(false)
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/leads">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Import Leads</h1>
          <p className="text-muted-foreground">Import leads from CSV or Excel file</p>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center justify-center gap-4">
        <div className={`flex items-center gap-2 ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>1</div>
          <span className="font-medium">Upload</span>
        </div>
        <div className={`w-16 h-0.5 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`} />
        <div className={`flex items-center gap-2 ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>2</div>
          <span className="font-medium">Map Fields</span>
        </div>
        <div className={`w-16 h-0.5 ${step >= 3 ? 'bg-blue-600' : 'bg-gray-200'}`} />
        <div className={`flex items-center gap-2 ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>3</div>
          <span className="font-medium">Complete</span>
        </div>
      </div>

      {/* Step 1: Upload */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Upload File</CardTitle>
            <CardDescription>Upload a CSV or Excel file containing lead data</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              {file ? (
                <div className="flex items-center justify-center gap-4">
                  <FileSpreadsheet className="h-12 w-12 text-green-600" />
                  <div className="text-left">
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => setFile(null)}>
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <>
                  <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium mb-2">Drop your file here</p>
                  <p className="text-muted-foreground mb-4">or click to browse</p>
                  <Input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    className="max-w-xs mx-auto"
                    onChange={handleFileChange}
                  />
                </>
              )}
            </div>

            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-blue-900">File Requirements</p>
                  <ul className="text-sm text-blue-700 mt-2 space-y-1">
                    <li>• Supported formats: CSV, XLSX, XLS</li>
                    <li>• Maximum file size: 10MB</li>
                    <li>• First row should contain column headers</li>
                    <li>• Required fields: Name, Phone</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="flex justify-between">
              <Button variant="outline" asChild>
                <a href="/templates/leads-import-template.csv" download>
                  <Download className="mr-2 h-4 w-4" />
                  Download Template
                </a>
              </Button>
              <Button onClick={handleUpload} disabled={!file}>
                Continue to Mapping
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Map Fields */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>Map Fields</CardTitle>
            <CardDescription>Match your CSV columns to CRM fields</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <FileSpreadsheet className="h-5 w-5 text-gray-600" />
                <span className="font-medium">{file?.name}</span>
              </div>
              <p className="text-sm text-muted-foreground">Found 6 columns, 150 rows</p>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4 font-medium text-sm text-muted-foreground">
                <div>CSV Column</div>
                <div>CRM Field</div>
                <div>Status</div>
              </div>
              {mappings.map((mapping, index) => (
                <div key={mapping.csvField} className="grid grid-cols-3 gap-4 items-center">
                  <div className="flex items-center gap-2">
                    <Table className="h-4 w-4 text-gray-400" />
                    <span>{mapping.csvField}</span>
                    {mapping.required && <span className="text-red-500">*</span>}
                  </div>
                  <Select 
                    value={mapping.crmField} 
                    onValueChange={(value) => {
                      const newMappings = [...mappings]
                      newMappings[index].crmField = value
                      setMappings(newMappings)
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Don't import</SelectItem>
                      {crmFields.map((field) => (
                        <SelectItem key={field} value={field}>{field}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <div>
                    {mapping.crmField ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : mapping.required ? (
                      <AlertCircle className="h-5 w-5 text-red-500" />
                    ) : (
                      <span className="text-sm text-muted-foreground">Optional</span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {importing && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Importing leads...</span>
                  <span>{progress}%</span>
                </div>
                <Progress value={progress} />
              </div>
            )}

            <div className="flex justify-between">
              <Button variant="outline" onClick={() => setStep(1)}>
                Back
              </Button>
              <Button onClick={handleImport} disabled={importing}>
                {importing ? 'Importing...' : 'Start Import'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Complete */}
      {step === 3 && (
        <Card>
          <CardContent className="py-12 text-center">
            <CheckCircle2 className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Import Complete!</h2>
            <p className="text-muted-foreground mb-6">
              Successfully imported 150 leads into your CRM.
            </p>
            
            <div className="bg-gray-50 rounded-lg p-4 max-w-md mx-auto mb-6">
              <div className="grid grid-cols-2 gap-4 text-left">
                <div>
                  <p className="text-sm text-muted-foreground">Total Records</p>
                  <p className="text-xl font-bold">150</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Successfully Imported</p>
                  <p className="text-xl font-bold text-green-600">148</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Duplicates Skipped</p>
                  <p className="text-xl font-bold text-yellow-600">2</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Errors</p>
                  <p className="text-xl font-bold text-red-600">0</p>
                </div>
              </div>
            </div>

            <div className="flex justify-center gap-3">
              <Button variant="outline" onClick={() => { setStep(1); setFile(null); setProgress(0); }}>
                Import More
              </Button>
              <Link href="/leads">
                <Button>View Leads</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
