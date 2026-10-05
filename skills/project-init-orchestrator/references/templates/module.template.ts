/**
 * NestJS Module Template
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 */

import { Module } from "@nestjs/common";
import { MongooseModule } from "@nestjs/mongoose";
import { {{Entity}}sController } from "./{{entities}}.controller";
import { {{Entity}}sService } from "./{{entities}}.service";
import { {{Entity}}, {{Entity}}Schema } from "./schemas/{{entity}}.schema";

@Module({
  imports: [
    MongooseModule.forFeature([
      { name: {{Entity}}.name, schema: {{Entity}}Schema },
    ]),
  ],
  controllers: [{{Entity}}sController],
  providers: [{{Entity}}sService],
  exports: [{{Entity}}sService],
})
export class {{Entity}}sModule {}
