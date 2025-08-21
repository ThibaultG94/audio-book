import { render, screen } from '@testing-library/react'
import { FileUpload } from '@/components/FileUpload'

describe('FileUpload', () => {
  it('renders upload area', () => {
    render(
      <FileUpload 
        onFileUploaded={() => {}} 
        isLoading={false} 
      />
    )
    
    expect(screen.getByText(/Upload PDF or EPUB file/i)).toBeInTheDocument()
  })
  
  it('shows loading state', () => {
    render(
      <FileUpload 
        onFileUploaded={() => {}} 
        isLoading={true} 
      />
    )
    
    expect(screen.getByRole('status')).toBeInTheDocument()
  })
})