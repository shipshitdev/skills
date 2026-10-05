/**
 * NestJS Service Template
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 */

import { Injectable, NotFoundException } from "@nestjs/common";
import { InjectModel } from "@nestjs/mongoose";
import { Model } from "mongoose";
import { {{Entity}}, {{Entity}}Document } from "./schemas/{{entity}}.schema";
import { Create{{Entity}}Dto } from "./dto/create-{{entity}}.dto";
import { Update{{Entity}}Dto } from "./dto/update-{{entity}}.dto";

@Injectable()
export class {{Entity}}sService {
  constructor(
    @InjectModel({{Entity}}.name) private {{entity}}Model: Model<{{Entity}}Document>,
  ) {}

  async create(create{{Entity}}Dto: Create{{Entity}}Dto, userId: string): Promise<{{Entity}}> {
    const {{entity}} = new this.{{entity}}Model({
      ...create{{Entity}}Dto,
      userId,
    });
    return {{entity}}.save();
  }

  async findAll(userId: string): Promise<{{Entity}}[]> {
    const query = this.{{entity}}Model.find({ userId }).sort({ createdAt: -1 });
    return query.then((docs) => docs);
  }

  async findOne(id: string, userId: string): Promise<{{Entity}}> {
    const query = this.{{entity}}Model.findOne({ _id: id, userId });
    const {{entity}} = await query.then((doc) => doc);

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
    const query = this.{{entity}}Model.findOneAndUpdate(
      { _id: id, userId },
      update{{Entity}}Dto,
      { new: true },
    );
    const {{entity}} = await query.then((doc) => doc);

    if (!{{entity}}) {
      throw new NotFoundException(`{{Entity}} with ID ${id} not found`);
    }

    return {{entity}};
  }

  async remove(id: string, userId: string): Promise<void> {
    const query = this.{{entity}}Model.deleteOne({ _id: id, userId });
    const result = await query.then((res) => res);

    if (result.deletedCount === 0) {
      throw new NotFoundException(`{{Entity}} with ID ${id} not found`);
    }
  }
}
