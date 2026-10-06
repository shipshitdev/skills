/**
 * NestJS Service Test Template (Vitest)
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 *
 * Requires unplugin-swc in vitest.config.ts so decorator metadata reaches Nest DI.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { Test, TestingModule } from "@nestjs/testing";
import { NotFoundException } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import { {{Entity}}sService } from "./{{entities}}.service";

describe("{{Entity}}sService", () => {
  let service: {{Entity}}sService;

  const prismaMock = {
    {{entity}}: {
      create: vi.fn(),
      findMany: vi.fn(),
      findFirst: vi.fn(),
      updateMany: vi.fn(),
      deleteMany: vi.fn(),
    },
  };

  const mockUserId = "user-123";
  const mock{{Entity}} = {
    id: "{{entity}}-123",
    title: "Test {{Entity}}",
    userId: mockUserId,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        {{Entity}}sService,
        { provide: PrismaService, useValue: prismaMock },
      ],
    }).compile();

    service = module.get<{{Entity}}sService>({{Entity}}sService);
  });

  it("should be defined", () => {
    expect(service).toBeDefined();
  });

  describe("create", () => {
    it("should create a {{entity}} owned by the user", async () => {
      prismaMock.{{entity}}.create.mockResolvedValue(mock{{Entity}});

      const result = await service.create({ title: "Test {{Entity}}" }, mockUserId);

      expect(result).toEqual(mock{{Entity}});
      expect(prismaMock.{{entity}}.create).toHaveBeenCalledWith({
        data: { title: "Test {{Entity}}", userId: mockUserId },
      });
    });
  });

  describe("findAll", () => {
    it("should return all {{entities}} for a user", async () => {
      prismaMock.{{entity}}.findMany.mockResolvedValue([mock{{Entity}}]);

      const result = await service.findAll(mockUserId);

      expect(result).toEqual([mock{{Entity}}]);
      expect(prismaMock.{{entity}}.findMany).toHaveBeenCalledWith({
        where: { userId: mockUserId },
        orderBy: { createdAt: "desc" },
      });
    });
  });

  describe("findOne", () => {
    it("should return a {{entity}} by id", async () => {
      prismaMock.{{entity}}.findFirst.mockResolvedValue(mock{{Entity}});

      const result = await service.findOne("{{entity}}-123", mockUserId);

      expect(result).toEqual(mock{{Entity}});
      expect(prismaMock.{{entity}}.findFirst).toHaveBeenCalledWith({
        where: { id: "{{entity}}-123", userId: mockUserId },
      });
    });

    it("should throw NotFoundException if {{entity}} not found", async () => {
      prismaMock.{{entity}}.findFirst.mockResolvedValue(null);

      await expect(
        service.findOne("nonexistent", mockUserId),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe("update", () => {
    it("should update a {{entity}}", async () => {
      prismaMock.{{entity}}.updateMany.mockResolvedValue({ count: 1 });
      prismaMock.{{entity}}.findFirst.mockResolvedValue({
        ...mock{{Entity}},
        title: "Updated",
      });

      const result = await service.update(
        "{{entity}}-123",
        { title: "Updated" },
        mockUserId,
      );

      expect(result.title).toBe("Updated");
    });

    it("should throw NotFoundException if {{entity}} not found", async () => {
      prismaMock.{{entity}}.updateMany.mockResolvedValue({ count: 0 });

      await expect(
        service.update("nonexistent", { title: "Test" }, mockUserId),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe("remove", () => {
    it("should delete a {{entity}}", async () => {
      prismaMock.{{entity}}.deleteMany.mockResolvedValue({ count: 1 });

      await expect(
        service.remove("{{entity}}-123", mockUserId),
      ).resolves.not.toThrow();
    });

    it("should throw NotFoundException if {{entity}} not found", async () => {
      prismaMock.{{entity}}.deleteMany.mockResolvedValue({ count: 0 });

      await expect(
        service.remove("nonexistent", mockUserId),
      ).rejects.toThrow(NotFoundException);
    });
  });
});
