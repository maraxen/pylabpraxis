import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:praxis_lab_management/src/features/assetManagement/application/bloc/asset_management_bloc.dart';

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
            Center(child: Placeholder(child: Text('Instruments Tab Content'))),
            // Placeholder for Labware Instances content
            Center(
              child: Placeholder(child: Text('Labware Instances Tab Content')),
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
