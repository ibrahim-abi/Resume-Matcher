import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_ORIGIN || 'http://127.0.0.1:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    console.log('Forwarding AI Engine Scoring request to backend with extended timeout...');
    
    // Manual proxy with extended timeout
    const response = await fetch(`${BACKEND_URL}/api/v1/engine/score`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      // Set a long timeout (3 minutes)
      signal: AbortSignal.timeout(180000),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errorData.detail || 'Engine scoring failed at backend' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error: any) {
    console.error('AI Engine Scoring Route Handler Error:', error);
    
    if (error.name === 'TimeoutError') {
      return NextResponse.json(
        { detail: 'AI Engine Scoring timed out after 180 seconds. Please check the backend logs.' },
        { status: 504 }
      );
    }
    
    return NextResponse.json(
      { detail: `Internal Proxy Error: ${error.message}` },
      { status: 500 }
    );
  }
}
