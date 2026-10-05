/**
 * NestJS Service Test Template (Vitest)
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { Test, TestingModule } from "@nestjs/testing";
import { getModelToken } from "@nestjs/mongoose";
import { NotFoundException } from "@nestjs/common";
import { {{Entity}}sService } from "./{{entities}}.service";
import { {{Entity}} } from "./schemas/{{entity}}.schema";

describe("{{Entity}}sService", () => {
  let service: {{Entity}}sService;
  let mockModel: any;

  const mockUserId = "user-123";
  const mock{{Entity}} = {
    _id: "{{entity}}-123",
    title: "Test {{Entity}}",
    userId: mockUserId,
    createdAt: new Date(),
    save: vi.fn().mockResolvedValue(this),
  };

  beforeEach(async () => {
    mockModel = {
      new: vi.fn().mockResolvedValue(mock{{Entity}}),
      constructor: vi.fn().mockResolvedValue(mock{{Entity}}),
      find: vi.fn(),
      findOne: vi.fn(),
      findOneAndUpdate: vi.fn(),
      deleteOne: vi.fn(),
    };

    // Mock the constructor behavior
    mockModel.mockImplementation = vi.fn().mockReturnValue(mock{{Entity}});

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        {{Entity}}sService,
        {
          provide: getModelToken({{Entity}}.name),
          useValue: {
            ...mockModel,
            new: vi.fn().mockImplementation((data) => ({
              ...data,
              save: vi.fn().mockResolvedValue({ ...data, _id: "new-id" }),
            })),
          },
        },
      ],
    }).compile();

    service = module.get<{{Entity}}sService>({{Entity}}sService);
  });

  it("should be defined", () => {
    expect(service).toBeDefined();
  });

  describe("findAll", () => {
    it("should return all {{entities}} for a user", async () => {
      const mock{{Entity}}s = [mock{{Entity}}];
      mockModel.find.mockReturnValue({
        sort: vi.fn().mockReturnValue({
          exec: vi.fn().mockResolvedValue(mock{{Entity}}s),
        }),
      });

      const result = await service.findAll(mockUserId);

      expect(result).toEqual(mock{{Entity}}s);
      expect(mockModel.find).toHaveBeenCalledWith({ userId: mockUserId });
    });
  });

  describe("findOne", () => {
    it("should return a {{entity}} by id", async () => {
      mockModel.findOne.mockReturnValue({
        exec: vi.fn().mockResolvedValue(mock{{Entity}}),
      });

      const result = await service.findOne("{{entity}}-123", mockUserId);

      expect(result).toEqual(mock{{Entity}});
      expect(mockModel.findOne).toHaveBeenCalledWith({
        _id: "{{entity}}-123",
        userId: mockUserId,
      });
    });

    it("should throw NotFoundException if {{entity}} not found", async () => {
      mockModel.findOne.mockReturnValue({
        exec: vi.fn().mockResolvedValue(null),
      });

      await expect(
        service.findOne("nonexistent", mockUserId),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe("update", () => {
    it("should update a {{entity}}", async () => {
      const updated{{Entity}} = { ...mock{{Entity}}, title: "Updated" };
      mockModel.findOneAndUpdate.mockReturnValue({
        exec: vi.fn().mockResolvedValue(updated{{Entity}}),
      });

      const result = await service.update(
        "{{entity}}-123",
        { title: "Updated" },
        mockUserId,
      );

      expect(result.title).toBe("Updated");
    });

    it("should throw NotFoundException if {{entity}} not found", async () => {
      mockModel.findOneAndUpdate.mockReturnValue({
        exec: vi.fn().mockResolvedValue(null),
      });

      await expect(
        service.update("nonexistent", { title: "Test" }, mockUserId),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe("remove", () => {
    it("should delete a {{entity}}", async () => {
      mockModel.deleteOne.mockReturnValue({
        exec: vi.fn().mockResolvedValue({ deletedCount: 1 }),
      });

      await expect(
        service.remove("{{entity}}-123", mockUserId),
      ).resolves.not.toThrow();
    });

    it("should throw NotFoundException if {{entity}} not found", async () => {
      mockModel.deleteOne.mockReturnValue({
        exec: vi.fn().mockResolvedValue({ deletedCount: 0 }),
      });

      await expect(
        service.remove("nonexistent", mockUserId),
      ).rejects.toThrow(NotFoundException);
    });
  });
});
