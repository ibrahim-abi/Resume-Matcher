import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_ORIGIN || 'http://127.0.0.1:8000';

/**
 * Route Handler for Standard Flow Preview.
 * Bypasses standard proxy for extended timeout (180s).
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    console.log('Forwarding Standard Flow PREVIEW to backend with extended timeout (180s)...');
    
    const response = await fetch(`${BACKEND_URL}/api/v1/resumes/improve/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(180000),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errorData.detail || 'Standard preview failed at backend' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error: any) {
    console.error('Standard Preview Route Handler Error:', error);
    if (error.name === 'TimeoutError') {
      return NextResponse.json(
        { detail: 'Standard Preview timed out after 180 seconds. The model might be slow or the job description is very long.' },
        { status: 504 }
      );
    }
    return NextResponse.json({ detail: `Internal Proxy Error: ${error.message}` }, { status: 500 });
  }
}
