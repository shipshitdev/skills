/**
 * NestJS E2E Test Template (Vitest + Supertest)
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 *
 * Requires: npm install -D supertest @types/supertest
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach } from "vitest";
import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication, ValidationPipe } from "@nestjs/common";
import * as request from "supertest";
import { AppModule } from "../app.module";
import { MongoMemoryServer } from "mongodb-memory-server";
import { MongooseModule } from "@nestjs/mongoose";

describe("{{Entity}}s E2E", () => {
  let app: INestApplication;
  let mongod: MongoMemoryServer;
  let authToken: string;

  // Mock auth token for testing
  const mockAuthToken = "Bearer test-token";

  beforeAll(async () => {
    // Start in-memory MongoDB
    mongod = await MongoMemoryServer.create();
    const mongoUri = mongod.getUri();

    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    })
      .overrideProvider("MONGODB_URI")
      .useValue(mongoUri)
      .compile();

    app = moduleFixture.createNestApplication();

    // Apply same configuration as main.ts
    app.useGlobalPipes(
      new ValidationPipe({
        whitelist: true,
        transform: true,
        forbidNonWhitelisted: true,
      })
    );

    await app.init();
  });

  afterAll(async () => {
    await app.close();
    await mongod.stop();
  });

  describe("POST /{{entities}}", () => {
    it("should create a new {{entity}}", async () => {
      const create{{Entity}}Dto = {
        title: "Test {{Entity}}",
        // Add other required fields
      };

      const response = await request(app.getHttpServer())
        .post("/{{entities}}")
        .set("Authorization", mockAuthToken)
        .send(create{{Entity}}Dto)
        .expect(201);

      expect(response.body).toHaveProperty("_id");
      expect(response.body.title).toBe(create{{Entity}}Dto.title);
    });

    it("should return 401 without auth token", async () => {
      await request(app.getHttpServer())
        .post("/{{entities}}")
        .send({ title: "Test" })
        .expect(401);
    });

    it("should return 400 for invalid data", async () => {
      await request(app.getHttpServer())
        .post("/{{entities}}")
        .set("Authorization", mockAuthToken)
        .send({}) // Missing required fields
        .expect(400);
    });
  });

  describe("GET /{{entities}}", () => {
    it("should return all {{entities}} for user", async () => {
      const response = await request(app.getHttpServer())
        .get("/{{entities}}")
        .set("Authorization", mockAuthToken)
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
    });

    it("should return 401 without auth token", async () => {
      await request(app.getHttpServer())
        .get("/{{entities}}")
        .expect(401);
    });
  });

  describe("GET /{{entities}}/:id", () => {
    let created{{Entity}}Id: string;

    beforeEach(async () => {
      // Create a {{entity}} first
      const response = await request(app.getHttpServer())
        .post("/{{entities}}")
        .set("Authorization", mockAuthToken)
        .send({ title: "Test {{Entity}}" });

      created{{Entity}}Id = response.body._id;
    });

    it("should return a {{entity}} by id", async () => {
      const response = await request(app.getHttpServer())
        .get(`/{{entities}}/${created{{Entity}}Id}`)
        .set("Authorization", mockAuthToken)
        .expect(200);

      expect(response.body._id).toBe(created{{Entity}}Id);
    });

    it("should return 404 for non-existent {{entity}}", async () => {
      await request(app.getHttpServer())
        .get("/{{entities}}/nonexistent-id")
        .set("Authorization", mockAuthToken)
        .expect(404);
    });
  });

  describe("PATCH /{{entities}}/:id", () => {
    let created{{Entity}}Id: string;

    beforeEach(async () => {
      const response = await request(app.getHttpServer())
        .post("/{{entities}}")
        .set("Authorization", mockAuthToken)
        .send({ title: "Test {{Entity}}" });

      created{{Entity}}Id = response.body._id;
    });

    it("should update a {{entity}}", async () => {
      const updateDto = { title: "Updated {{Entity}}" };

      const response = await request(app.getHttpServer())
        .patch(`/{{entities}}/${created{{Entity}}Id}`)
        .set("Authorization", mockAuthToken)
        .send(updateDto)
        .expect(200);

      expect(response.body.title).toBe(updateDto.title);
    });

    it("should return 404 for non-existent {{entity}}", async () => {
      await request(app.getHttpServer())
        .patch("/{{entities}}/nonexistent-id")
        .set("Authorization", mockAuthToken)
        .send({ title: "Updated" })
        .expect(404);
    });
  });

  describe("DELETE /{{entities}}/:id", () => {
    let created{{Entity}}Id: string;

    beforeEach(async () => {
      const response = await request(app.getHttpServer())
        .post("/{{entities}}")
        .set("Authorization", mockAuthToken)
        .send({ title: "Test {{Entity}}" });

      created{{Entity}}Id = response.body._id;
    });

    it("should delete a {{entity}}", async () => {
      await request(app.getHttpServer())
        .delete(`/{{entities}}/${created{{Entity}}Id}`)
        .set("Authorization", mockAuthToken)
        .expect(200);

      // Verify deletion
      await request(app.getHttpServer())
        .get(`/{{entities}}/${created{{Entity}}Id}`)
        .set("Authorization", mockAuthToken)
        .expect(404);
    });

    it("should return 404 for non-existent {{entity}}", async () => {
      await request(app.getHttpServer())
        .delete("/{{entities}}/nonexistent-id")
        .set("Authorization", mockAuthToken)
        .expect(404);
    });
  });
});
