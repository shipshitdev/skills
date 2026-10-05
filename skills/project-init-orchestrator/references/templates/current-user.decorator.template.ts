/**
 * Current User Decorator Template
 *
 * Place this at: api/apps/api/src/auth/decorators/current-user.decorator.ts
 */

import { createParamDecorator, ExecutionContext } from "@nestjs/common";

export interface CurrentUserPayload {
  userId: string;
  sessionId?: string;
}

export const CurrentUser = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): CurrentUserPayload => {
    const request = ctx.switchToHttp().getRequest();
    return request.user;
  },
);
