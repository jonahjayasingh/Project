// proxy.ts — put in project root

let hits = new Map<string, { count: number; time: number }>();

const LIMIT = 100;      // 50 requests
const WINDOW = 60_000; // 60 seconds

const handler = async (req: Request) => {
  const ip =
    req.headers.get('x-forwarded-for')?.split(',')[0] ??
    'unknown';

  const now = Date.now();
  const record = hits.get(ip);

  if (!record || now - record.time > WINDOW) {
    hits.set(ip, { count: 1, time: now });
    return;
  }

  if (record.count >= LIMIT) {
    return new Response(JSON.stringify({ error: 'Rate limit exceeded' }), {
      status: 429,
    });
  }

  record.count++;
};

export const config = {
  matcher: ['/api/:path*'],
};

export default handler;
