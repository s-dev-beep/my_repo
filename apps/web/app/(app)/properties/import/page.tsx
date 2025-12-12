'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import { 
  ArrowLeft, Upload, FileSpreadsheet, Download, CheckCircle2, 
  AlertCircle, Building2
} from 'lucide-react'

export default function ImportPropertiesPage() {
  const [step, setStep] = useState(1)
  const [file, setFile] = useState<File | null>(null)
  const [importing, setImporting] = useState(false)
  const [progress, setProgress] = useState(0)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleImport = async () => {
    setImporting(true)
    setStep(2)
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
        <Link href="/properties">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Import Properties</h1>
          <p className="text-muted-foreground">Bulk import properties from CSV or Excel</p>
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
          <span className="font-medium">Processing</span>
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
            <CardDescription>Upload a CSV or Excel file containing property data</CardDescription>
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
                  <Button variant="ghost" onClick={() => setFile(null)}>Remove</Button>
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
                  <p className="font-medium text-blue-900">Required Columns</p>
                  <ul className="text-sm text-blue-700 mt-2 space-y-1">
                    <li>• Title, Address, District, City</li>
                    <li>• Price, Type (sale/rent), Property Type</li>
                    <li>• Area (m²), Bedrooms, Bathrooms</li>
                    <li>• Optional: Latitude, Longitude, Features, Images</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="flex justify-between">
              <Button variant="outline" asChild>
                <a href="/templates/properties-import-template.csv" download>
                  <Download className="mr-2 h-4 w-4" />
                  Download Template
                </a>
              </Button>
              <Button onClick={handleImport} disabled={!file}>
                Start Import
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Processing */}
      {step === 2 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Building2 className="h-16 w-16 text-blue-500 mx-auto mb-4 animate-pulse" />
            <h2 className="text-xl font-bold mb-4">Importing Properties...</h2>
            <div className="max-w-md mx-auto space-y-2">
              <Progress value={progress} />
              <p className="text-sm text-muted-foreground">{progress}% complete</p>
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
              Successfully imported 45 properties into your catalog.
            </p>
            
            <div className="bg-gray-50 rounded-lg p-4 max-w-md mx-auto mb-6">
              <div className="grid grid-cols-2 gap-4 text-left">
                <div>
                  <p className="text-sm text-muted-foreground">Total Records</p>
                  <p className="text-xl font-bold">48</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Successfully Imported</p>
                  <p className="text-xl font-bold text-green-600">45</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Duplicates Skipped</p>
                  <p className="text-xl font-bold text-yellow-600">2</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Errors</p>
                  <p className="text-xl font-bold text-red-600">1</p>
                </div>
              </div>
            </div>

            <div className="flex justify-center gap-3">
              <Button variant="outline" onClick={() => { setStep(1); setFile(null); setProgress(0); }}>
                Import More
              </Button>
              <Link href="/properties">
                <Button>View Properties</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
