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

interface CookieResponse {
  append(name: string, value: string): unknown;
}

@Injectable()
export class AuthGuard implements CanActivate {
  constructor(private readonly authService: AuthService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const http = context.switchToHttp();
    const request = http.getRequest<AuthenticatedRequest>();
    const { headers, response: session } = await this.authService.auth.api.getSession({
      headers: fromNodeHeaders(request.headers),
      returnHeaders: true,
    });

    // Better Auth renews sessions close to expiry (and clears invalid cookies) through
    // Set-Cookie headers. Forward them or the browser keeps the stale cookie.
    const response = http.getResponse<CookieResponse>();
    for (const cookie of headers.getSetCookie()) {
      response.append("Set-Cookie", cookie);
    }

    if (!session) {
      throw new UnauthorizedException("Not signed in");
    }

    request.user = { userId: session.user.id, sessionId: session.session.id };
    return true;
  }
}
