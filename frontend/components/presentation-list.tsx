"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Edit, Trash2, FileIcon as FilePresentation, Sparkles, FileText, Loader2 } from "lucide-react"
import type { Presentation } from "@/lib/types"
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious, PaginationEllipsis } from "@/components/ui/pagination"
import { motion } from "framer-motion"
import { AnimatedContainer, AnimatedItem } from "@/components/ui-elements"
import { api } from "@/lib/api"
import { toast } from "sonner"

export default function PresentationList() {
  const [presentations, setPresentations] = useState<Presentation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [view, setView] = useState<'grid' | 'list'>('grid')
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [previewImages, setPreviewImages] = useState<Record<string, string>>({})
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [total, setTotal] = useState(0)
  const [statusFilter, setStatusFilter] = useState<'all' | 'finished' | 'in_progress'>('all')

  useEffect(() => {
    // Load presentations from the API
    loadPresentations(page, pageSize, statusFilter)
  }, [page, pageSize, statusFilter])

  const loadPresentations = async (
    pageParam = page,
    sizeParam = pageSize,
    statusParam = statusFilter
  ) => {
    setIsLoading(true)
    try {
      const data = await api.getPresentations(pageParam, sizeParam, statusParam)
      const fetchedPresentations = data.items
      setTotal(data.total)
      
      // Show all presentations, regardless of whether they have thumbnails
      setPresentations(fetchedPresentations)

      // Create preview images map from the thumbnail URLs in the API response
      // If a presentation doesn't have a thumbnail, it will use the placeholder
      const previewMap: Record<string, string> = {}
      fetchedPresentations.forEach(p => {
        if (p.thumbnailUrl) {
          previewMap[p.id.toString()] = p.thumbnailUrl
        }
      })
      setPreviewImages(previewMap)
      setError(null)
    } catch (err) {
      setError("Failed to load presentations")
      console.error("Error loading presentations:", err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!window.confirm("Are you sure")) return

    try {
      const success = await api.deletePresentation(id)

      if (success) {
        // Remove presentation locally for snappier UI
        setPresentations(presentations.filter((p) => p.id !== id))
        // Reload from server to ensure we stay in sync
        await loadPresentations()
        toast.success("Presentation deleted successfully")
      } else {
        toast.error("Failed to delete presentation")
      }
    } catch (error) {
      console.error(`Error deleting presentation ${id}:`, error)
      toast.error("Failed to delete presentation")
    }
  }

  const handleDeleteSelected = async () => {
    if (selected.size === 0) return
    if (!window.confirm("Delete selected presentations?")) return

    for (const id of selected) {
      await api.deletePresentation(id)
    }
    setSelected(new Set())
    await loadPresentations()
    toast.success("Selected presentations deleted")
  }

  const toggleSelect = (id: string) => {
    const newSet = new Set(selected)
    if (newSet.has(id)) newSet.delete(id)
    else newSet.add(id)
    setSelected(newSet)
  }

  const selectAll = (checked: boolean) => {
    if (checked) {
      setSelected(new Set(presentations.map((p) => p.id.toString())))
    } else {
      setSelected(new Set())
    }
  }

  // Helper function to generate pagination items with ellipsis
  const generatePaginationItems = () => {
    const totalPages = Math.ceil(total / pageSize) || 1;
    const items = [];
    const maxVisiblePages = 5;
    
    if (totalPages <= maxVisiblePages) {
      // Show all pages if total is less than or equal to max visible
      for (let i = 1; i <= totalPages; i++) {
        items.push(
          <PaginationItem key={i}>
            <PaginationLink 
              href="#" 
              isActive={page === i} 
              onClick={(e) => {
                e.preventDefault();
                setPage(i);
              }}
            >
              {i}
            </PaginationLink>
          </PaginationItem>
        );
      }
    } else {
      // Always show first page
      items.push(
        <PaginationItem key={1}>
          <PaginationLink 
            href="#" 
            isActive={page === 1} 
            onClick={(e) => {
              e.preventDefault();
              setPage(1);
            }}
          >
            1
          </PaginationLink>
        </PaginationItem>
      );

      // Show ellipsis and middle pages
      if (page > 3) {
        items.push(
          <PaginationItem key="ellipsis-start">
            <PaginationEllipsis />
          </PaginationItem>
        );
      }

      // Show current page and surrounding pages
      const start = Math.max(2, page - 1);
      const end = Math.min(totalPages - 1, page + 1);
      
      for (let i = start; i <= end; i++) {
        items.push(
          <PaginationItem key={i}>
            <PaginationLink 
              href="#" 
              isActive={page === i} 
              onClick={(e) => {
                e.preventDefault();
                setPage(i);
              }}
            >
              {i}
            </PaginationLink>
          </PaginationItem>
        );
      }

      // Show ellipsis before last page if needed
      if (page < totalPages - 2) {
        items.push(
          <PaginationItem key="ellipsis-end">
            <PaginationEllipsis />
          </PaginationItem>
        );
      }

      // Always show last page if more than one page
      if (totalPages > 1) {
        items.push(
          <PaginationItem key={totalPages}>
            <PaginationLink 
              href="#" 
              isActive={page === totalPages} 
              onClick={(e) => {
                e.preventDefault();
                setPage(totalPages);
              }}
            >
              {totalPages}
            </PaginationLink>
          </PaginationItem>
        );
      }
    }
    
    return items;
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12" data-testid="presentations-loading">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
        <span className="ml-2 text-gray-600 dark:text-gray-300">Loading presentations...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12 bg-red-50/50 dark:bg-red-900/20 rounded-xl border border-dashed border-red-200 dark:border-red-700" data-testid="presentations-error">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-md mx-auto"
        >
          <h2 className="text-xl font-semibold mb-3 text-red-700">Failed to Load Presentations</h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">{error}</p>
          <Button 
            className="bg-primary hover:bg-primary-600 text-white font-medium px-6 py-2 rounded-full"
            onClick={() => loadPresentations()}
            data-testid="retry-button"
          >
            Try Again
          </Button>
        </motion.div>
      </div>
    )
  }

  if (presentations.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50/50 dark:bg-gray-800/50 rounded-xl border border-dashed border-gray-200 dark:border-gray-700" data-testid="no-presentations-message">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-md mx-auto"
        >
          <FilePresentation className="h-16 w-16 mx-auto text-gray-300 mb-4" />
          <h2 className="text-2xl font-semibold mb-3 text-gray-700 dark:text-gray-200">No presentations yet</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">Create your first presentation to get started with AI-powered slides</p>
          <Link href="/create">
            <Button 
              className="bg-primary hover:bg-primary-600 text-white font-medium px-6 py-2 rounded-full transition-all duration-300 shadow-lg hover:shadow-primary-500/25"
              data-testid="create-presentation-button"
            >
              Create Presentation
            </Button>
          </Link>
        </motion.div>
      </div>
    )
  }

  return (
    <AnimatedContainer>
      <div className="flex justify-between items-center mb-4">
        <div className="space-x-2 flex items-center">
          <Button
            variant={view === 'grid' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setView('grid')}
            data-testid="view-grid-button"
          >
            Grid
          </Button>
          <Button
            variant={view === 'list' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setView('list')}
            data-testid="view-list-button"
          >
            List
          </Button>
          <label className="ml-4 text-sm flex items-center gap-1">
            <input
              type="checkbox"
              onChange={(e) => selectAll(e.target.checked)}
              checked={selected.size === presentations.length && presentations.length > 0}
              data-testid="select-all-checkbox"
            />
            Select All
          </label>
        </div>
        {selected.size > 0 && (
          <Button
            variant="destructive"
            size="sm"
            onClick={handleDeleteSelected}
            data-testid="delete-selected-button"
          >
            Delete Selected
          </Button>
        )}
      </div>
      {view === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="presentations-grid">
          {presentations.map((presentation) => (
            <AnimatedItem key={presentation.id}>
              <Card
                className="slide-card overflow-hidden border border-gray-100 dark:border-gray-700 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm"
                data-testid={`presentation-card-${presentation.id}`}
              >
              <CardHeader className="pb-2 relative">
                <input
                  type="checkbox"
                  className="absolute left-3 top-3"
                  checked={selected.has(presentation.id.toString())}
                  onChange={() => toggleSelect(presentation.id.toString())}
                  data-testid="select-presentation-checkbox"
                />
                <div className="absolute top-3 right-3">
                  {presentation.researchMethod === "ai" ? (
                    <div className="bg-primary-100 text-primary-600 text-xs px-2 py-1 rounded-full flex items-center gap-1" data-testid="research-method-ai">
                      <Sparkles size={12} />
                      AI Research
                    </div>
                  ) : (
                    <div className="bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 text-xs px-2 py-1 rounded-full flex items-center gap-1" data-testid="research-method-manual">
                      <FileText size={12} />
                      Manual
                    </div>
                  )}
                </div>
                <CardTitle className="text-xl font-bold text-gray-800 dark:text-gray-100" data-testid="presentation-name">{presentation.name}</CardTitle>
                <p className="text-sm text-gray-500 dark:text-gray-400" data-testid="presentation-author">By {presentation.author}</p>
                <div className="hidden" data-testid="presentation-id">ID: {presentation.id}</div>
              </CardHeader>
              <CardContent>
                <div className="w-full aspect-[16/9] bg-gradient-to-br from-primary-50 to-secondary-50 rounded-lg flex items-center justify-center mb-4 overflow-hidden group relative">
                  <img
                    src={previewImages[presentation.id.toString()] ?? `/placeholder.svg?height=180&width=320&query=colorful presentation slide with abstract shapes`}
                    alt="Presentation thumbnail"
                    className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                    data-testid="presentation-thumbnail"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end justify-center pb-4">
                    <p className="text-white text-sm font-medium" data-testid="presentation-slide-count">{presentation.slides && presentation.slides.length ? presentation.slides.length : 0} slides</p>
                  </div>
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  <p data-testid="presentation-created-date">Created: {typeof window !== 'undefined' && presentation.createdAt ? 
                    new Date(presentation.createdAt).toLocaleDateString() : 'N/A'}</p>
                  {presentation.topic && <p className="truncate" data-testid="presentation-topic">Topic: {presentation.topic}</p>}
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Link href={`/edit/${presentation.id}`}>
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex items-center gap-1 hover:bg-primary-50 hover:text-primary-600 transition-colors"
                    data-testid="edit-presentation-button"
                  >
                    <Edit size={16} />
                    Edit
                  </Button>
                </Link>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1 hover:bg-red-50 hover:text-red-600 transition-colors"
                  onClick={() => handleDelete(presentation.id.toString())}
                  data-testid="delete-presentation-button"
                >
                  <Trash2 size={16} />
                  Delete
                </Button>
              </CardFooter>
            </Card>
          </AnimatedItem>
        ))}
        </div>
      ) : (
        <Table data-testid="presentations-table">
          <TableHeader>
            <TableRow>
              <TableHead>
                <input type="checkbox" onChange={(e) => selectAll(e.target.checked)} checked={selected.size === presentations.length && presentations.length > 0} />
              </TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Author</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Slides</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {presentations.map((p) => (
              <TableRow key={p.id} data-testid={`presentation-row-${p.id}`}>
                <TableCell>
                  <input type="checkbox" checked={selected.has(p.id.toString())} onChange={() => toggleSelect(p.id.toString())} data-testid="select-presentation-checkbox" />
                </TableCell>
                <TableCell className="font-medium">{p.name}</TableCell>
                <TableCell>{p.author}</TableCell>
                <TableCell>{typeof window !== 'undefined' && p.createdAt ? new Date(p.createdAt).toLocaleDateString() : 'N/A'}</TableCell>
                <TableCell>{p.slides ? p.slides.length : 0}</TableCell>
                <TableCell className="space-x-2">
                  <Link href={`/edit/${p.id}`}> <Button variant="outline" size="sm" data-testid="edit-presentation-button">Edit</Button></Link>
                  <Button variant="outline" size="sm" onClick={() => handleDelete(p.id.toString())} data-testid="delete-presentation-button">Delete</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
      <div className="flex items-center justify-between mt-6">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label htmlFor="status-filter" className="text-sm font-medium text-gray-700 dark:text-gray-300">Status:</label>
            <select
              id="status-filter"
              value={statusFilter}
              onChange={(e) => {
                setPage(1)
                setStatusFilter(e.target.value as any)
              }}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              data-testid="status-filter-select"
            >
              <option value="all">All</option>
              <option value="finished">Finished</option>
              <option value="in_progress">In Progress</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            <label htmlFor="page-size" className="text-sm font-medium text-gray-700 dark:text-gray-300">Per page:</label>
            <select
              id="page-size"
              value={pageSize}
              onChange={(e) => {
                setPage(1)
                setPageSize(parseInt(e.target.value))
              }}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              data-testid="page-size-select"
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-300">
            Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, total)} of {total} presentations
          </div>
        </div>
        
        {Math.ceil(total / pageSize) > 1 && (
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious 
                  href="#" 
                  onClick={(e) => {
                    e.preventDefault();
                    if (page > 1) setPage(page - 1);
                  }}
                  className={page === 1 ? "cursor-not-allowed opacity-50" : "cursor-pointer"}
                  data-disabled={page === 1}
                />
              </PaginationItem>
              {generatePaginationItems()}
              <PaginationItem>
                <PaginationNext 
                  href="#" 
                  onClick={(e) => {
                    e.preventDefault();
                    if (page < Math.ceil(total / pageSize)) setPage(page + 1);
                  }}
                  className={page === Math.ceil(total / pageSize) ? "cursor-not-allowed opacity-50" : "cursor-pointer"}
                  data-disabled={page === Math.ceil(total / pageSize)}
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        )}
      </div>
    </AnimatedContainer>
  )
}
