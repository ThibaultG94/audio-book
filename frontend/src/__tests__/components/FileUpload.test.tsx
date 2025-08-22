import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FileUpload } from '@/components/FileUpload'

// Mock the API module
jest.mock('@/lib/api', () => ({
  api: {
    uploadFile: jest.fn(),
  },
}))

describe('FileUpload Component', () => {
  const mockOnFileUploaded = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders upload area with correct text', () => {
    render(
      <FileUpload 
        onFileUploaded={mockOnFileUploaded} 
        isLoading={false} 
      />
    )
    
    expect(screen.getByText(/Upload PDF or EPUB file/i)).toBeInTheDocument()
    expect(screen.getByText(/Drag & drop or click to select/i)).toBeInTheDocument()
  })
  
  it('shows loading state when isLoading is true', () => {
    render(
      <FileUpload 
        onFileUploaded={mockOnFileUploaded} 
        isLoading={true} 
      />
    )
    
    // Should show spinner
    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })

  it('displays error message when upload fails', async () => {
    const { api } = await import('@/lib/api')
    ;(api.uploadFile as jest.Mock).mockRejectedValue(new Error('Upload failed'))

    render(
      <FileUpload 
        onFileUploaded={mockOnFileUploaded} 
        isLoading={false} 
      />
    )

    // Create a test file
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    const input = screen.getByLabelText(/upload/i, { selector: 'input' })

    await userEvent.upload(input, file)

    await waitFor(() => {
      expect(screen.getByText(/Upload failed/i)).toBeInTheDocument()
    })
  })
})