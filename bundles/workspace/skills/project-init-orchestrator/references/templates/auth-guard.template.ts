/**
 * Better Auth Session Guard Template
 *
 * Place this at: api/apps/api/src/auth/guards/auth.guard.ts
 *
 * Requires AuthService (auth-service.template.ts) from a global AuthModule, so feature
 * modules can use @UseGuards(AuthGuard) without importing it.
 */

import type { IncomingHttpHeaders } from "node:http";
import { CanActivate, ExecutionContext, Injectable, UnauthorizedException } from "@nestjs/common";
import { fromNodeHeaders } from "better-auth/node";
import { AuthService } from "../auth.service";
import type { CurrentUserPayload } from "../decorators/current-user.decorator";

interface AuthenticatedRequest {
  headers: IncomingHttpHeaders;
  user?: CurrentUserPayload;
}

@Injectable()
export class AuthGuard implements CanActivate {
  constructor(private readonly authService: AuthService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<AuthenticatedRequest>();
    const session = await this.authService.auth.api.getSession({
      headers: fromNodeHeaders(request.headers),
    });

    if (!session) {
      throw new UnauthorizedException("Not signed in");
    }

    request.user = { userId: session.user.id, sessionId: session.session.id };
    return true;
  }
}
