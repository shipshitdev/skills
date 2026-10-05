/**
 * Clerk Auth Guard Template
 *
 * Place this at: api/apps/api/src/auth/guards/clerk-auth.guard.ts
 */

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
} from "@nestjs/common";
import { Clerk } from "@clerk/clerk-sdk-node";

@Injectable()
export class ClerkAuthGuard implements CanActivate {
  private clerk: Clerk;

  constructor() {
    this.clerk = new Clerk({
      secretKey: process.env.CLERK_SECRET_KEY || "",
    });
  }

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const authHeader = request.headers.authorization;

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      throw new UnauthorizedException("No authorization token provided");
    }

    const token = authHeader.replace("Bearer ", "");

    try {
      const session = await this.clerk.verifyToken(token);
      request.user = {
        userId: session.sub,
        sessionId: session.sid,
      };
      return true;
    } catch (error) {
      throw new UnauthorizedException("Invalid or expired token");
    }
  }
}
