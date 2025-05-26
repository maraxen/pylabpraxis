// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:praxis/src/features/assetManagement/application/bloc/asset_management_bloc.dart';

class AssetManagementScreen extends StatelessWidget {
  const AssetManagementScreen({super.key});

  static const String routeName = '/assetManagement';

  @override
  Widget build(BuildContext context) {
    // It's assumed that AssetManagementBloc will be provided higher up in the widget tree
    // For example, in the AppRouter or a dedicated BlocProvider setup.
    // final bloc = context.read<AssetManagementBloc>();

    return DefaultTabController(
      length: 3, // Number of tabs
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Asset Management'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Instruments'),
              Tab(text: 'Labware Instances'),
              Tab(text: 'Labware Definitions'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            // Placeholder for Instruments content
            Center(
              child: Placeholder(
                child: Text('Instruments Tab Content'),
              ),
            ),
            // Placeholder for Labware Instances content
            Center(
              child: Placeholder(
                child: Text('Labware Instances Tab Content'),
              ),
            ),
            // Placeholder for Labware Definitions content
            Center(
              child: Placeholder(
                child: Text('Labware Definitions Tab Content'),
              ),
            ),
          ],
        ),
        // TODO(user): Add a FloatingActionButton to add new assets,
        // which would then trigger events on the AssetManagementBloc.
      ),
    );
  }
}
