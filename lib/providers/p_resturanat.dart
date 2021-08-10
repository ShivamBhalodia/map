import 'dart:ffi';

import 'package:flutter/cupertino.dart';
import 'package:hostel_app/models/getItems.dart';
import 'package:hostel_app/models/getRestuarant.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class P_Restuarant with ChangeNotifier {
  List<GetRestuarant> items = [];
  List<GetItems> itemss = [];
  List<GetRestuarant> searchitem = [];
  List<GetItems> searchitems = [];
  Future<void> fetchrestuarant() async {
    print("fetchshops");
    try {
      final List<GetRestuarant> loadedshop = [];
      final response = await http.get(
        Uri.parse('http://bd72ae609002.ngrok.io/get_restaurants'),
        headers: {
          "Content-Type": "application/json",
        },
      );
      final res = json.decode(response.body);
      print('res');
      print(res);
      res.forEach(
        (f) => loadedshop.add(
          GetRestuarant(
            id: f['id'],
            phone: f['phone'],
            address: f['address'],
            o_name: f['Owner_name'],
            loggedin_with: f['loggedin_with'],
            r_name: f['Restaurant_name'],
          ),
        ),
      );
      items = loadedshop;
      print(items);
      print(res);
    } catch (error) {
      throw (error);
    }
  }

  GetRestuarant findByIdShop(int id) {
    return items.firstWhere((element) => element.id == id);
  }

  Future<void> fetchItems(int id) async {
    print("fetchitems");
    try {
      final List<GetItems> loadedshop = [];
      final response = await http.get(
        Uri.parse('http://bd72ae609002.ngrok.io/get_items/$id'),
        headers: {
          "Content-Type": "application/json",
        },
      );
      final res = json.decode(response.body);
      print('res');
      print(res);
      res.forEach(
        (f) => loadedshop.add(
          GetItems(
            id: f['id'],
            name: f['Name'],
            description: f['Description'],
            price: f['Price'],
            category: f['Category'],
          ),
        ),
      );
      itemss = loadedshop;
      print(itemss);
      print(res);
    } catch (error) {
      throw (error);
    }
  }

  GetItems findByIdItems(int id) {
    return itemss.firstWhere((element) => element.id == id);
  }

  Future<void> searchfromitems(String search, int id) async {
    print("serachfromitems $search");
    print(id);
    final response = await http.get(
      Uri.parse('http://bd72ae609002.ngrok.io/get_items_byname/$id/$search'),
    );
    final res = json.decode(response.body);
    final List<GetItems> loadedshop = [];
    print('res');
    print(res);
    res.forEach(
      (f) => loadedshop.add(
        GetItems(
          id: f['id'],
          name: f['Name'],
          description: f['Description'],
          price: f['Price'],
          category: f['Category'],
        ),
      ),
    );
    print(res);
    print(loadedshop);
    loadedshop.forEach((element) {
      print("element is ");
      print(element);
      if (element.name == search) searchitems.add(element);
      print("it is added");
    });
    notifyListeners();
    print("serachfromitems last");
  }

  late String temp;
  Future<void> searchShop(String search) async {
    try {
      final response = await http.get(
        Uri.parse('http://bd72ae609002.ngrok.io/get_restaurant_byname/$search'),
      );
      final res = json.decode(response.body);
      final List<GetRestuarant> loadedshop = [];
      print("res of serachshop is $res");
      res.forEach((f) {
        loadedshop.add(
          GetRestuarant(
            id: f['id'],
            phone: f['phone'],
            address: f['address'],
            o_name: f['Owner_name'],
            loggedin_with: f['loggedin_with'],
            r_name: f['Restaurant_name'],
          ),
        );
      });
      print(loadedshop);
      loadedshop.forEach((element) {
        print("element is ");
        print(element);
        searchitem.add(element);
        print("it is added");
      });
      notifyListeners();
    } catch (error) {
      throw (error);
    }
  }
}
