import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_ORIGIN || 'http://127.0.0.1:8000';

/**
 * Route Handler for Resume Uploads.
 * Bypasses standard proxy to allow for longer timeouts (180s).
 */
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    
    console.log('Forwarding Resume Upload to backend with extended timeout (180s)...');
    
    const response = await fetch(`${BACKEND_URL}/api/v1/resumes/upload`, {
      method: 'POST',
      body: formData,
      // Signal timeout after 3 minutes for heavy parsing/OCR tasks
      signal: AbortSignal.timeout(180000),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errorData.detail || 'Resume upload failed at backend' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error: any) {
    console.error('Resume Upload Route Handler Error:', error);
    
    if (error.name === 'TimeoutError') {
      return NextResponse.json(
        { detail: 'Resume upload timed out after 180 seconds. The file might be too complex or the backend is busy.' },
        { status: 504 }
      );
    }
    
    return NextResponse.json(
      { detail: `Internal Proxy Error: ${error.message}` },
      { status: 500 }
    );
  }
}
