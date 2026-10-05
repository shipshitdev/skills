/**
 * NestJS Controller Template
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 */

import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  Query,
  UseGuards,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiBearerAuth, ApiQuery } from "@nestjs/swagger";
import { {{Entity}}sService } from "./{{entities}}.service";
import { Create{{Entity}}Dto } from "./dto/create-{{entity}}.dto";
import { Update{{Entity}}Dto } from "./dto/update-{{entity}}.dto";
import { ClerkAuthGuard } from "../auth/guards/clerk-auth.guard";
import { CurrentUser } from "../auth/decorators/current-user.decorator";

@ApiTags("{{entities}}")
@ApiBearerAuth()
@UseGuards(ClerkAuthGuard)
@Controller("{{entities}}")
export class {{Entity}}sController {
  constructor(private readonly {{entities}}Service: {{Entity}}sService) {}

  @Post()
  @ApiOperation({ summary: "Create a new {{entity}}" })
  create(
    @Body() create{{Entity}}Dto: Create{{Entity}}Dto,
    @CurrentUser() user: { userId: string },
  ) {
    return this.{{entities}}Service.create(create{{Entity}}Dto, user.userId);
  }

  @Get()
  @ApiOperation({ summary: "Get all {{entities}}" })
  findAll(@CurrentUser() user: { userId: string }) {
    return this.{{entities}}Service.findAll(user.userId);
  }

  @Get(":id")
  @ApiOperation({ summary: "Get a {{entity}} by ID" })
  findOne(
    @Param("id") id: string,
    @CurrentUser() user: { userId: string },
  ) {
    return this.{{entities}}Service.findOne(id, user.userId);
  }

  @Patch(":id")
  @ApiOperation({ summary: "Update a {{entity}}" })
  update(
    @Param("id") id: string,
    @Body() update{{Entity}}Dto: Update{{Entity}}Dto,
    @CurrentUser() user: { userId: string },
  ) {
    return this.{{entities}}Service.update(id, update{{Entity}}Dto, user.userId);
  }

  @Delete(":id")
  @ApiOperation({ summary: "Delete a {{entity}}" })
  remove(
    @Param("id") id: string,
    @CurrentUser() user: { userId: string },
  ) {
    return this.{{entities}}Service.remove(id, user.userId);
  }
}
