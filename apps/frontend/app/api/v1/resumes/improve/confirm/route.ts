import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_ORIGIN || 'http://127.0.0.1:8000';

/**
 * Route Handler for Standard Flow Confirmation.
 * Bypasses standard proxy for extended timeout (120s).
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    console.log('Forwarding Standard Flow CONFIRM to backend with extended timeout (120s)...');
    
    const response = await fetch(`${BACKEND_URL}/api/v1/resumes/improve/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(120000),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errorData.detail || 'Standard confirmation failed at backend' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error: any) {
    console.error('Standard Confirm Route Handler Error:', error);
    if (error.name === 'TimeoutError') {
      return NextResponse.json(
        { detail: 'Standard Confirm timed out after 120 seconds. Backend might be processing auxiliary messages.' },
        { status: 504 }
      );
    }
    return NextResponse.json({ detail: `Internal Proxy Error: ${error.message}` }, { status: 500 });
  }
}
