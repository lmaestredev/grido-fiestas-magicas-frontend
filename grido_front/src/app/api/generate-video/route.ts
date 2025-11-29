import { NextRequest, NextResponse } from "next/server";
import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";

// Initialize Redis (Upstash for serverless)
const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

export interface VideoRequest {
  nombre: string;
  parentesco: string;
  email: string;
  provincia: string;
  queHizo: string;
  recuerdoEspecial: string;
  pedidoNocheMagica: string;
}

export async function POST(request: NextRequest) {
  try {
    // Verify API secret
    const authHeader = request.headers.get("authorization");
    const expectedAuth = `Bearer ${process.env.VIDEO_API_SECRET}`;
    
    if (authHeader !== expectedAuth) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    // Parse request body
    const body: VideoRequest = await request.json();

    // Validate required fields
    if (!body.nombre || !body.email || !body.provincia) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    // Generate unique video ID
    const videoId = nanoid(12);

    // Create job object
    const job = {
      videoId,
      status: "pending",
      data: body,
      createdAt: new Date().toISOString(),
    };

    // Store job in Redis
    await redis.set(`job:${videoId}`, JSON.stringify(job));
    
    // Add to processing queue
    await redis.lpush("video:queue", videoId);

    // Trigger worker (if using webhook-based workers)
    if (process.env.WORKER_WEBHOOK_URL) {
      fetch(process.env.WORKER_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ videoId }),
      }).catch(console.error);
    }

    return NextResponse.json({
      success: true,
      message: "Video generation queued",
      videoId,
    });
  } catch (error) {
    console.error("Error in generate-video API:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

// Optional: GET endpoint to check video status
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const videoId = searchParams.get("videoId");

  if (!videoId) {
    return NextResponse.json(
      { error: "Missing videoId" },
      { status: 400 }
    );
  }

  try {
    const jobData = await redis.get(`job:${videoId}`);
    
    if (!jobData) {
      return NextResponse.json(
        { error: "Video not found" },
        { status: 404 }
      );
    }

    return NextResponse.json(jobData);
  } catch (error) {
    console.error("Error fetching video status:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

