import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import { 
  Upload, 
  Search, 
  FileText, 
  Download, 
  MoreVertical,
  Edit,
  Trash2,
  Eye,
  BookOpen,
  Database,
  Zap,
  FileCheck
} from 'lucide-react';
import { apiService } from '../services/api';
import { KBDocument } from '../types';

export function KnowledgeBase() {
  const [searchTerm, setSearchTerm] = useState('');
  const [documents] = useState<KBDocument[]>(kbDocuments);
  const [selectedDoc, setSelectedDoc] = useState<KBDocument | null>(null);

  const filteredDocuments = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.content_preview?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getFileIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return '📄';
      case 'markdown':
      case 'md':
        return '📝';
      case 'txt':
        return '📋';
      default:
        return '📁';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const kbStats = {
    totalDocuments: documents.length,
    totalSize: documents.reduce((sum, doc) => sum + doc.file_size, 0),
    vectorized: documents.filter(doc => doc.vector_id).length,
    categories: new Set(documents.map(doc => doc.file_type)).size
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Knowledge Base</h1>
          <p className="text-slate-500 mt-1">
            Manage documents and train your AI agent with relevant information
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export All
          </Button>
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <Upload className="w-4 h-4 mr-2" />
                Upload Document
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Upload New Document</DialogTitle>
                <DialogDescription>
                  Add a new document to your knowledge base for AI training
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Document Title</label>
                  <Input placeholder="Enter document title" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">File Upload</label>
                  <div className="border-2 border-dashed border-slate-200 rounded-lg p-8 text-center">
                    <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                    <p className="text-sm text-slate-600 mb-2">
                      Drag and drop your file here, or click to browse
                    </p>
                    <p className="text-xs text-slate-400">
                      Supports PDF, DOC, TXT, MD files up to 10MB
                    </p>
                    <Button variant="outline" className="mt-3">
                      Choose File
                    </Button>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <input type="checkbox" id="auto-vectorize" className="rounded" />
                  <label htmlFor="auto-vectorize" className="text-sm">
                    Automatically vectorize document for AI search
                  </label>
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline">Cancel</Button>
                <Button>Upload Document</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">Total Documents</p>
                <p className="text-2xl font-bold text-slate-900">{kbStats.totalDocuments}</p>
              </div>
              <BookOpen className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">Total Size</p>
                <p className="text-2xl font-bold text-slate-900">{formatFileSize(kbStats.totalSize)}</p>
              </div>
              <Database className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">Vectorized</p>
                <p className="text-2xl font-bold text-slate-900">{kbStats.vectorized}</p>
              </div>
              <Zap className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">File Types</p>
                <p className="text-2xl font-bold text-slate-900">{kbStats.categories}</p>
              </div>
              <FileCheck className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="p-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <Input
              placeholder="Search documents by title or content..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Documents Table */}
      <Card>
        <CardHeader>
          <CardTitle>Documents ({filteredDocuments.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Document</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Size</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Updated</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredDocuments.map((doc) => (
                <TableRow key={doc.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">
                        {getFileIcon(doc.file_type)}
                      </div>
                      <div>
                        <p className="font-medium text-slate-900">{doc.title}</p>
                        <p className="text-sm text-slate-500 line-clamp-2">
                          {doc.content_preview}
                        </p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{doc.file_type}</Badge>
                  </TableCell>
                  <TableCell className="text-sm">{formatFileSize(doc.file_size)}</TableCell>
                  <TableCell>
                    <Badge variant={doc.vector_id ? 'default' : 'secondary'}>
                      {doc.vector_id ? 'Vectorized' : 'Processing'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {new Date(doc.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => setSelectedDoc(doc)}>
                          <Eye className="w-4 h-4 mr-2" />
                          View Details
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Download className="w-4 h-4 mr-2" />
                          Download
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Edit className="w-4 h-4 mr-2" />
                          Edit Metadata
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Zap className="w-4 h-4 mr-2" />
                          Re-vectorize
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-red-600">
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Document Details Dialog */}
      <Dialog open={!!selectedDoc} onOpenChange={() => setSelectedDoc(null)}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Document Details</DialogTitle>
            <DialogDescription>
              Complete information for {selectedDoc?.title}
            </DialogDescription>
          </DialogHeader>
          {selectedDoc && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-slate-900 mb-2">Document Information</h4>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Title:</span> {selectedDoc.title}</p>
                      <p><span className="font-medium">Type:</span> {selectedDoc.file_type}</p>
                      <p><span className="font-medium">Size:</span> {formatFileSize(selectedDoc.file_size)}</p>
                      <p><span className="font-medium">Vector ID:</span> {selectedDoc.vector_id}</p>
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-slate-900 mb-2">Processing Status</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Document Uploaded</span>
                        <Badge variant="default">✓</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Text Extracted</span>
                        <Badge variant="default">✓</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Vectorized</span>
                        <Badge variant={selectedDoc.vector_id ? 'default' : 'secondary'}>
                          {selectedDoc.vector_id ? '✓' : '⏳'}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Indexed for Search</span>
                        <Badge variant={selectedDoc.vector_id ? 'default' : 'secondary'}>
                          {selectedDoc.vector_id ? '✓' : '⏳'}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="font-medium text-slate-900 mb-2">Content Preview</h4>
                <div className="bg-slate-50 p-4 rounded-lg max-h-48 overflow-y-auto">
                  <p className="text-sm text-slate-700 whitespace-pre-wrap">
                    {selectedDoc.content_preview}
                  </p>
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setSelectedDoc(null)}>
                  Close
                </Button>
                <Button variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
                <Button>
                  <Zap className="w-4 h-4 mr-2" />
                  Re-vectorize
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
