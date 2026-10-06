/**
 * NestJS Module Template
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 *
 * PrismaModule is global, so PrismaService is injectable without importing it here.
 */

import { Module } from "@nestjs/common";
import { {{Entity}}sController } from "./{{entities}}.controller";
import { {{Entity}}sService } from "./{{entities}}.service";

@Module({
  controllers: [{{Entity}}sController],
  providers: [{{Entity}}sService],
  exports: [{{Entity}}sService],
})
export class {{Entity}}sModule {}
