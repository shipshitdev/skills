/**
 * NestJS Controller Test Template (Vitest)
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { Test, TestingModule } from "@nestjs/testing";
import { {{Entity}}sController } from "./{{entities}}.controller";
import { {{Entity}}sService } from "./{{entities}}.service";
import { Create{{Entity}}Dto } from "./dto/create-{{entity}}.dto";
import { Update{{Entity}}Dto } from "./dto/update-{{entity}}.dto";

describe("{{Entity}}sController", () => {
  let controller: {{Entity}}sController;
  let service: {{Entity}}sService;

  const mockUser = { userId: "user-123" };
  const mock{{Entity}} = {
    _id: "{{entity}}-123",
    title: "Test {{Entity}}",
    userId: mockUser.userId,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  const mock{{Entity}}sService = {
    create: vi.fn(),
    findAll: vi.fn(),
    findOne: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [{{Entity}}sController],
      providers: [
        {
          provide: {{Entity}}sService,
          useValue: mock{{Entity}}sService,
        },
      ],
    }).compile();

    controller = module.get<{{Entity}}sController>({{Entity}}sController);
    service = module.get<{{Entity}}sService>({{Entity}}sService);

    // Reset mocks
    vi.clearAllMocks();
  });

  it("should be defined", () => {
    expect(controller).toBeDefined();
  });

  describe("create", () => {
    it("should create a new {{entity}}", async () => {
      const createDto: Create{{Entity}}Dto = {
        title: "New {{Entity}}",
      };

      mock{{Entity}}sService.create.mockResolvedValue(mock{{Entity}});

      const result = await controller.create(createDto, mockUser);

      expect(service.create).toHaveBeenCalledWith(createDto, mockUser.userId);
      expect(result).toEqual(mock{{Entity}});
    });
  });

  describe("findAll", () => {
    it("should return all {{entities}} for user", async () => {
      const {{entities}} = [mock{{Entity}}];
      mock{{Entity}}sService.findAll.mockResolvedValue({{entities}});

      const result = await controller.findAll(mockUser);

      expect(service.findAll).toHaveBeenCalledWith(mockUser.userId);
      expect(result).toEqual({{entities}});
    });
  });

  describe("findOne", () => {
    it("should return a single {{entity}}", async () => {
      mock{{Entity}}sService.findOne.mockResolvedValue(mock{{Entity}});

      const result = await controller.findOne("{{entity}}-123", mockUser);

      expect(service.findOne).toHaveBeenCalledWith("{{entity}}-123", mockUser.userId);
      expect(result).toEqual(mock{{Entity}});
    });
  });

  describe("update", () => {
    it("should update a {{entity}}", async () => {
      const updateDto: Update{{Entity}}Dto = { title: "Updated" };
      const updated{{Entity}} = { ...mock{{Entity}}, ...updateDto };

      mock{{Entity}}sService.update.mockResolvedValue(updated{{Entity}});

      const result = await controller.update("{{entity}}-123", updateDto, mockUser);

      expect(service.update).toHaveBeenCalledWith("{{entity}}-123", updateDto, mockUser.userId);
      expect(result.title).toBe("Updated");
    });
  });

  describe("remove", () => {
    it("should delete a {{entity}}", async () => {
      mock{{Entity}}sService.remove.mockResolvedValue(undefined);

      await controller.remove("{{entity}}-123", mockUser);

      expect(service.remove).toHaveBeenCalledWith("{{entity}}-123", mockUser.userId);
    });
  });
});
