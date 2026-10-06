/**
 * NestJS Service Template (Prisma)
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 */

import { Injectable, NotFoundException } from "@nestjs/common";
import type { {{Entity}} } from "../../generated/prisma/client";
import { PrismaService } from "../../prisma/prisma.service";
import { Create{{Entity}}Dto } from "./dto/create-{{entity}}.dto";
import { Update{{Entity}}Dto } from "./dto/update-{{entity}}.dto";

@Injectable()
export class {{Entity}}sService {
  constructor(private readonly prisma: PrismaService) {}

  async create(create{{Entity}}Dto: Create{{Entity}}Dto, userId: string): Promise<{{Entity}}> {
    return this.prisma.{{entity}}.create({
      data: { ...create{{Entity}}Dto, userId },
    });
  }

  async findAll(userId: string): Promise<{{Entity}}[]> {
    return this.prisma.{{entity}}.findMany({
      where: { userId },
      orderBy: { createdAt: "desc" },
    });
  }

  async findOne(id: string, userId: string): Promise<{{Entity}}> {
    const {{entity}} = await this.prisma.{{entity}}.findFirst({
      where: { id, userId },
    });

    if (!{{entity}}) {
      throw new NotFoundException(`{{Entity}} with ID ${id} not found`);
    }

    return {{entity}};
  }

  async update(
    id: string,
    update{{Entity}}Dto: Update{{Entity}}Dto,
    userId: string,
  ): Promise<{{Entity}}> {
    // updateMany scopes the write to the owner in a single statement
    const result = await this.prisma.{{entity}}.updateMany({
      where: { id, userId },
      data: update{{Entity}}Dto,
    });

    if (result.count === 0) {
      throw new NotFoundException(`{{Entity}} with ID ${id} not found`);
    }

    return this.findOne(id, userId);
  }

  async remove(id: string, userId: string): Promise<void> {
    const result = await this.prisma.{{entity}}.deleteMany({
      where: { id, userId },
    });

    if (result.count === 0) {
      throw new NotFoundException(`{{Entity}} with ID ${id} not found`);
    }
  }
}
