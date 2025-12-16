import { NextRequest, NextResponse } from "next/server";
import { Redis } from "@upstash/redis";

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

/**
 * GET endpoint para consultar el estado de un video.
 * El POST fue eliminado porque ahora se escribe directamente en Redis desde sendGreeting.
 */

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

